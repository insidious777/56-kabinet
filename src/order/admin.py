from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from order.models import Cart, Customer, Order, CartItem, DeliveryAddress, OrderTransaction, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ('menu_item', 'additions_list', 'count', 'total_amount')
    max_num = 0
    exclude = ('additions',)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description=_('Additions'))
    def additions_list(self, obj):
        rendered_additions = []

        for addition in obj.additions.all():
            rendered_additions.append(f"""
                <div>
                    - <a href="{reverse('admin:menu_addition_change', args=[addition.id])}">{addition}</a>
                </div>
            """)

        return mark_safe(''.join(rendered_additions)) or '-'


@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    readonly_fields = ('session_key', 'total_amount')

    inlines = [
        CartItemInline,
    ]


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name')
    search_fields = ('name', 'phone_number')


class DeliveryAddressInline(admin.StackedInline):
    model = DeliveryAddress


class OrderTransactionInline(admin.StackedInline):
    model = OrderTransaction

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('additional_data', 'type', 'amount')

        return []


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    max_num = 0
    exclude = ('title',)
    fields = ('menu_item', 'price', 'volume', 'count', 'additions_list')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('menu_item', 'title', 'price', 'volume', 'count', 'additions_list')

        return ['additions_list']

    @admin.display(description=_('Additions'))
    def additions_list(self, obj):
        rendered_additions = []

        for addition_item in obj.addition_items.all():

            if addition_item.addition:
                rendered_addition = f"""
                    <div>
                        - <a href="{reverse('admin:menu_addition_change', args=[addition_item.addition.id])}">{addition_item}</a>
                    </div>
                """
            else:
                rendered_addition = f"<div>- {addition_item}</div>"

            rendered_additions.append(rendered_addition)

        return mark_safe(''.join(rendered_additions)) or '-'


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [
        DeliveryAddressInline,
        OrderTransactionInline,
        OrderItemInline,
    ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('session_key', 'customer', 'is_rejected', 'prepayment_required', 'payment_method',
                    'customer_comment', 'peoples_count')

        return []
