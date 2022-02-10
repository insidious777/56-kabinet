from django.utils.decorators import method_decorator
from django.views.generic import ListView

from menu.filters import MenuCategoryFilter
from menu.models import MenuCategory
from menu.repository.action import get_actual_actions
from menu.repository.menu_item import get_additions_to_show, get_menu_categories_to_show
from order.decorators import redirect_to_payment_if_needed
from order.repository.cart import get_menu_items_in_cart, get_cart_total_amount


@method_decorator(redirect_to_payment_if_needed, name='get')
class MainView(ListView):
    model = MenuCategory
    template_name = 'main.html'
    context_object_name = 'menu_categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context.update({
            'all_categories': get_menu_categories_to_show(),
            'additions': get_additions_to_show()
        })

        if not self.request.user.is_authenticated:
            session_key = self.request.session.session_key

            context.update({
                'actions': get_actual_actions(),
                'menu_items_in_cart': get_menu_items_in_cart(session_key),
                'total_amount': get_cart_total_amount(session_key),
            })

        return context

    def get_queryset(self):
        return MenuCategoryFilter(
            self.request.GET,
            super().get_queryset()
                .filter(show=True)
                .prefetch_related('menu_items')
                .order_by('order_index')
        ).qs


@method_decorator(redirect_to_payment_if_needed, name='get')
class AdditionsListView(ListView):
    model = MenuCategory
    template_name = 'additions.html'
    context_object_name = 'all_categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context.update({
            'additions': get_additions_to_show()
        })

        if not self.request.user.is_authenticated:
            session_key = self.request.session.session_key

            context.update({
                'actions': get_actual_actions(),
                'menu_items_in_cart': get_menu_items_in_cart(session_key),
                'total_amount': get_cart_total_amount(session_key),
            })

        return context

    def get_queryset(self):
        return super().get_queryset().filter(show=True).order_by('order_index')
