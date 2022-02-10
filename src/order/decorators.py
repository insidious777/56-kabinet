from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from order.repository.order import get_order_transaction_by_session_key


def redirect_to_payment_if_needed(func):

    @wraps(func)
    def payment_check(request, *args, **kwargs):
        order_transaction = get_order_transaction_by_session_key(request.session.session_key)

        if order_transaction and not order_transaction.is_paid():
            return redirect(reverse('order:payment'))

        return func(request, *args, **kwargs)

    return payment_check
