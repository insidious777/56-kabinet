import base64
import json

import pytest
from django.conf import settings
from django.core import mail
from django.urls import reverse

from liqpay import LiqPay
from menu.models import Addition
from order.repository.cart import add_menu_item_to_cart
from settings.repository import get_site_settings


@pytest.mark.django_db(reset_sequences=True)
def test_liqpay_callback(client, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    order = create_order(session.session_key, cart)

    data = base64.b64encode(json.dumps({
        'status': 'success',
        'order_id': order.id,

        # will be stored in additional data
        'liqpay_order_id': 'test_liqpay_order_id',
        'payment_id': 'test_payment_id',
        'paytype': 'pay',
        'refund_date_last': 'test_refund_date_last',
        'sender_card_type': 'test_sender_card_type',
        'sender_commission': 'test_sender_commission',
        'sender_first_name': 'test_sender_first_name',
        'sender_last_name': 'test_sender_last_name',
        'sender_phone': 'test_sender_phone',
        'token': 'test_token',
        'type': 'test_type',
    }).encode('utf-8')).decode('utf-8')

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    signature = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY +
        data +
        settings.LIQPAY_PRIVATE_KEY
    )

    request_data = {
        'data': data,
        'signature': signature
    }

    response = client.post(reverse('order_api:confirm_payment'), request_data)

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.transaction.is_paid()
    assert order.transaction.additional_data


@pytest.mark.django_db(reset_sequences=True)
def test_liqpay_callback_new_order_notification(client, admin_user, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.notify_users.add(admin_user)
    site_settings.save()

    order = create_order(session.session_key, cart)

    data = base64.b64encode(json.dumps({
        'status': 'success',
        'order_id': order.id,

        # will be stored in additional data
        'liqpay_order_id': 'test_liqpay_order_id',
        'payment_id': 'test_payment_id',
        'paytype': 'pay',
        'refund_date_last': 'test_refund_date_last',
        'sender_card_type': 'test_sender_card_type',
        'sender_commission': 'test_sender_commission',
        'sender_first_name': 'test_sender_first_name',
        'sender_last_name': 'test_sender_last_name',
        'sender_phone': 'test_sender_phone',
        'token': 'test_token',
        'type': 'test_type',
    }).encode('utf-8')).decode('utf-8')

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    signature = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY +
        data +
        settings.LIQPAY_PRIVATE_KEY
    )

    request_data = {
        'data': data,
        'signature': signature
    }

    response = client.post(reverse('order_api:confirm_payment'), request_data)

    assert response.status_code == 200

    # new order notification
    assert len(mail.outbox) == 1


@pytest.mark.django_db(reset_sequences=True)
def test_liqpay_callback_not_existing_order(client, admin_user, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.notify_users.add(admin_user)
    site_settings.save()

    order = create_order(session.session_key, cart)

    data = base64.b64encode(json.dumps({
        'status': 'success',
        'order_id': 666,

        # will be stored in additional data
        'liqpay_order_id': 'test_liqpay_order_id',
        'payment_id': 'test_payment_id',
        'paytype': 'pay',
        'refund_date_last': 'test_refund_date_last',
        'sender_card_type': 'test_sender_card_type',
        'sender_commission': 'test_sender_commission',
        'sender_first_name': 'test_sender_first_name',
        'sender_last_name': 'test_sender_last_name',
        'sender_phone': 'test_sender_phone',
        'token': 'test_token',
        'type': 'test_type',
    }).encode('utf-8')).decode('utf-8')

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    signature = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY +
        data +
        settings.LIQPAY_PRIVATE_KEY
    )

    request_data = {
        'data': data,
        'signature': signature
    }

    response = client.post(reverse('order_api:confirm_payment'), request_data)

    assert response.status_code == 404


@pytest.mark.django_db(reset_sequences=True)
def test_liqpay_callback_with_invalid_signature(client, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    order = create_order(session.session_key, cart)

    data = base64.b64encode(json.dumps({
        'status': 'success',
        'order_id': order.id,

        # will be stored in additional data
        'liqpay_order_id': 'test_liqpay_order_id',
        'payment_id': 'test_payment_id',
        'paytype': 'pay',
        'refund_date_last': 'test_refund_date_last',
        'sender_card_type': 'test_sender_card_type',
        'sender_commission': 'test_sender_commission',
        'sender_first_name': 'test_sender_first_name',
        'sender_last_name': 'test_sender_last_name',
        'sender_phone': 'test_sender_phone',
        'token': 'test_token',
        'type': 'test_type',
    }).encode('utf-8')).decode('utf-8')

    signature = 'invalid'

    request_data = {
        'data': data,
        'signature': signature
    }

    response = client.post(reverse('order_api:confirm_payment'), request_data)

    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_liqpay_callback_with_error_status_with_order_id(client, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    order = create_order(session.session_key, cart)

    data = base64.b64encode(json.dumps({
        'status': 'error',
        'err_code': 'order_id_empty',
        'err_description': 'Order_id is empty',
        'order_id': order.id
    }).encode('utf-8')).decode('utf-8')

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    signature = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY +
        data +
        settings.LIQPAY_PRIVATE_KEY
    )

    request_data = {
        'data': data,
        'signature': signature
    }

    response = client.post(reverse('order_api:confirm_payment'), request_data)

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.transaction.is_paid() is False
    assert order.transaction.additional_data


@pytest.mark.django_db(reset_sequences=True)
def test_liqpay_callback_with_error_status_without_order_id(client, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    order = create_order(session.session_key, cart)

    data = base64.b64encode(json.dumps({
        'status': 'error',
        'err_code': 'order_id_empty',
        'err_description': 'Order_id is empty',
    }).encode('utf-8')).decode('utf-8')

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    signature = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY +
        data +
        settings.LIQPAY_PRIVATE_KEY
    )

    request_data = {
        'data': data,
        'signature': signature
    }

    response = client.post(reverse('order_api:confirm_payment'), request_data)

    assert response.status_code == 404
