import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import DetailView

from common.decorators import redirect_if_authenticated
from fs_cabinet.settings import DEFAULT_LOGGER_NAME
from order.decorators import redirect_to_payment_if_needed
from order.handlers.liqpay import get_liqpay_payment_form
from order.repository.cart import get_cart, exclude_cart_items_from_cart_by_time_restrictions
from order.repository.order import get_order_transaction_by_session_key
from settings.repository import get_site_settings

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


@method_decorator(redirect_if_authenticated, name='get')
@method_decorator(redirect_to_payment_if_needed, name='get')
class CartView(DetailView):
    template_name = 'cart.html'
    context_object_name = 'cart'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_settings = get_site_settings()
        context.update({
            'delivery_time_within_city': site_settings.delivery_time_within_city.seconds // 60,
            'delivery_time_beyond_city': site_settings.delivery_time_beyond_city.seconds // 60
        })

        return context

    def get_object(self, queryset=None):
        return get_cart(self.request.session.session_key)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object is None:
            return redirect(reverse('menu:main'))

        excluded_cart_items = exclude_cart_items_from_cart_by_time_restrictions(self.object)
        context = self.get_context_data(object=self.object, excluded_cart_items=excluded_cart_items)
        return self.render_to_response(context)


@method_decorator(redirect_if_authenticated, name='get')
class PaymentView(DetailView):
    template_name = 'payment.html'
    context_object_name = 'order_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_transaction = context.get(self.context_object_name)

        logger.debug(f'request is secure: {self.request.is_secure()}')
        result_url = self.request.build_absolute_uri(reverse('menu:main'))
        server_url = self.request.build_absolute_uri(reverse('order_api:confirm_payment')),

        logger.debug(f'LIQPAY result_url: {result_url}')
        logger.debug(f'LIQPAY server_url: {server_url}')

        context.update({
            'payment_form': mark_safe(get_liqpay_payment_form(
                order_transaction,
                result_url=result_url,
                server_url=server_url,
            ))
        })
        return context

    def get_object(self, queryset=None):
        return get_order_transaction_by_session_key(self.request.session.session_key)

    def get(self, request, *args, **kwargs):
        self.object = order_transaction = self.get_object()

        if order_transaction is None or order_transaction.is_paid():
            return redirect(reverse('menu:main'))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
