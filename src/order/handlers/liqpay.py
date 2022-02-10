from django.conf import settings

from liqpay import LiqPay


def change_button_in_liqpay_form(cnb_form):
    return cnb_form.replace('//static.liqpay.ua/buttons/p1uk.radius.png', '/static/img/liqpay_buttons/logo-liqpay.png')


def get_liqpay_payment_form(order_transaction, result_url=None, server_url=None):
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    data = {
        'action': 'pay',
        'amount': str(order_transaction.amount),
        'currency': 'UAH',
        'description': order_transaction.get_payment_description(),
        'order_id': order_transaction.order_id,
        'version': '3',
        'language': 'uk',
    }

    if result_url:
        data.update({'result_url': result_url})

    if server_url:
        data.update({'server_url': server_url})

    cnb_form = liqpay.cnb_form(data)
    cnb_form = change_button_in_liqpay_form(cnb_form)
    return cnb_form


def verify_liqpay_signature(data, signature):
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    sign = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY +
        data +
        settings.LIQPAY_PRIVATE_KEY
    )

    return signature == sign
