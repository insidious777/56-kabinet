from decimal import Decimal

from django.core.validators import MinValueValidator, DecimalValidator
from django.db import models
from django.db.models import Sum, F
from django.utils.translation import gettext_lazy as _, pgettext_lazy, gettext

from order.constants import DeliveryMethods, OrderTransactionTypes, OrderTransactionStatuses
from order.validators import phone_number_validator
from order.constants import PaymentMethods


class Cart(models.Model):
    session_key = models.CharField(verbose_name=_('Session key'), max_length=40)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __str__(self):
        return gettext('Cart %(id)i') % {'id': self.id}

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_('Cart'), related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey('menu.MenuItem', verbose_name=_('Menu item'), related_name='cart_items', on_delete=models.CASCADE)

    count = models.PositiveSmallIntegerField(verbose_name=_('Count'), default=0)
    additions = models.ManyToManyField('menu.Addition', verbose_name=_('Additions'), related_name='cart_items', help_text=_("Hold down \"Control\", or \"Command\" on a Mac, to select more than one."))

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')

    def __str__(self):
        if self.menu_item.volume:
            return gettext('Cart item "%(menu_item_title)s %(menu_item_volume)s"') % {
                'menu_item_title': self.menu_item.title,
                'menu_item_volume': self.menu_item.volume,
            }

        return gettext('Cart item "%(menu_item_title)s"') % {'menu_item_title': self.menu_item.title}

    @property
    def total_amount(self):
        return Decimal((self.menu_item.price + (self.additions.aggregate(sum=Sum('price'))['sum'] or 0)) * self.count)


class Customer(models.Model):
    name = models.CharField(verbose_name=pgettext_lazy('Name', 'Human name'), max_length=100)
    phone_number = models.CharField(verbose_name=_('Phone number'), max_length=13, unique=True, validators=[phone_number_validator], help_text=_('Format: "+380123456789"'))

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return gettext('Customer %(phone_number)s') % {'phone_number': self.phone_number}


class Order(models.Model):
    session_key = models.CharField(verbose_name=_('Session key'), max_length=40)
    customer = models.ForeignKey(Customer, verbose_name=_('Customer'), related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)

    class DeliveryMethodChoices(models.TextChoices):
        COURIER = (DeliveryMethods.COURIER, _('Courier'))
        SELF_PICKUP = (DeliveryMethods.SELF_PICKUP, pgettext_lazy('delivery method', 'Self-pickup'))

    delivery_method = models.CharField(verbose_name=_('Delivery method'), max_length=50, choices=DeliveryMethodChoices.choices)
    self_pickup_time = models.DateTimeField(verbose_name=_('Self-pickup time'), null=True, blank=True)

    peoples_count = models.PositiveSmallIntegerField(verbose_name=_('Peoples count'), null=True, blank=True)
    customer_comment = models.TextField(verbose_name=_('Customer comment'), null=True, blank=True)

    class PaymentMethodsChoices(models.TextChoices):
        CASH = (PaymentMethods.CASH, _('Cash'))
        CARD = (PaymentMethods.CARD, _('Card'))
        LIQPAY = (PaymentMethods.LIQPAY, _('LiqPay'))

    payment_method = models.CharField(verbose_name=_('Payment method'), max_length=50, choices=PaymentMethodsChoices.choices)
    prepayment_required = models.BooleanField(verbose_name=_('Prepayment required'))

    is_rejected = models.BooleanField(verbose_name=_('Rejected'), default=False)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return gettext('Order %(id)i') % {'id': self.id}

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())

    def is_payment_required(self):
        return self.prepayment_required or (self.payment_method in [PaymentMethods.LIQPAY])


class DeliveryAddress(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), related_name='delivery_address', on_delete=models.CASCADE)

    settlement = models.CharField(verbose_name=pgettext_lazy('the name of city or village', 'Settlement'), max_length=100)
    street = models.CharField(verbose_name=_('Street'), max_length=100)
    building_number = models.CharField(verbose_name=_('Building number'), max_length=15)

    apartment_number = models.CharField(verbose_name=_('Apartment number'), max_length=15, null=True, blank=True)
    entrance_number = models.CharField(verbose_name=_('Entrance number'), max_length=15, null=True, blank=True)
    floor_number = models.CharField(verbose_name=_('Floor number'), max_length=15, null=True, blank=True)
    door_phone_number = models.CharField(verbose_name=_('Door phone number'), max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = _('Delivery address')
        verbose_name_plural = _('Delivery addresses')

    def __str__(self):
        return gettext('Delivery address')


class OrderTransaction(models.Model):
    order = models.OneToOneField(Order, verbose_name=_('Order'), related_name='transaction', on_delete=models.CASCADE)

    class Types(models.TextChoices):
        PREPAYMENT = (OrderTransactionTypes.PREPAYMENT, _('Prepayment'))
        FULL_PAYMENT = (OrderTransactionTypes.FULL_PAYMENT, _('Full payment'))

    type = models.CharField(verbose_name=_('Type'), max_length=50, choices=Types.choices)

    class Statuses(models.TextChoices):
        PAID = (OrderTransactionStatuses.PAID, _('Paid'))
        NOT_PAID = (OrderTransactionStatuses.NOT_PAID, _('Not paid'))

    status = models.CharField(verbose_name=_('Status'), max_length=50, choices=Statuses.choices, default=Statuses.NOT_PAID)

    amount = models.DecimalField(verbose_name=_('Amount'), max_digits=6, decimal_places=0, validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)])

    additional_data = models.JSONField(verbose_name=_('Additional data'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Order transaction')
        verbose_name_plural = _('Order transactions')

    def __str__(self):
        return gettext('Transaction ID %(id)i (Order ID %(order_id)i)') % {
            'id': self.id,
            'order_id': self.order_id,
        }

    def is_paid(self):
        return self.status == OrderTransactionStatuses.PAID

    def get_payment_description(self):
        if self.type == OrderTransactionTypes.PREPAYMENT:
            return _('Prepayment for order ID %(order_id)s') % {'order_id': self.order_id}

        elif self.type == OrderTransactionTypes.FULL_PAYMENT:
            return _('Payment for order ID %(order_id)s') % {'order_id': self.order_id}

        return _('Payment for order ID %(order_id)s') % {'order_id': self.order_id}


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=_('Order'), related_name='items', on_delete=models.CASCADE)

    menu_item = models.ForeignKey('menu.MenuItem', verbose_name=_('Menu item'), null=True, blank=True, on_delete=models.SET_NULL)

    title = models.CharField(verbose_name=_('Title'), max_length=100)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=6, decimal_places=0, validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)])
    count = models.PositiveSmallIntegerField(verbose_name=_('Count'))

    volume = models.CharField(verbose_name=_('Volume'), max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')

    def __str__(self):
        if self.volume:
            return gettext('Order item "%(item_title)s (%(item_volume)s)"') % {
                'item_title': self.title,
                'item_volume': self.volume,
            }

        return gettext('Order item "%(item_title)s"') % {'item_title': self.title}

    @property
    def total_amount(self):
        return Decimal((self.price + (self.addition_items.aggregate(sum=Sum('price'))['sum'] or 0)) * self.count)


class AdditionItem(models.Model):
    order_item = models.ForeignKey(OrderItem, verbose_name=_('Order item'), related_name='addition_items', on_delete=models.CASCADE)
    addition = models.ForeignKey('menu.Addition', verbose_name=_('Addition'), related_name='addition_items', null=True, blank=True, on_delete=models.SET_NULL)

    title = models.CharField(verbose_name=_('Title'), max_length=100)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=6, decimal_places=0, validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)])

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Addition item')
        verbose_name_plural = _('Addition items')

    def __str__(self):
        return gettext('Addition item "%(title)s"') % {'title': self.title}
