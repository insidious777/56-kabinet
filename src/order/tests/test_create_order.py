import datetime as dt
from decimal import Decimal

import pytest
from django.core import mail
from django.urls import reverse

from common.utils import get_local_now
from menu.models import Addition
from order.constants import DeliveryMethods, PaymentMethods, OrderTransactionTypes
from order.models import Cart, Customer, Order, DeliveryAddress, OrderItem, AdditionItem, OrderTransaction
from order.repository.cart import add_menu_item_to_cart
from order.tests.courier_delivery_order_test_parameters import COURIER_DELIVERY_TEST_PARAMETERS
from order.tests.self_pickup_order_test_parameters import SELF_PICKUP_ORDER_REQUESTS
from settings.repository import get_site_settings


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_forbidden_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('order_api:create_order'))
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize(
    'request_data,status_code,error_field,error_code',
    SELF_PICKUP_ORDER_REQUESTS
)
def test_create_order(client, create_cart, create_menu_item, mocker, request_data, status_code, error_field,
                      error_code):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    self_pickup_time = dt.datetime.utcnow() + site_settings.min_order_completion_time + dt.timedelta(seconds=1)
    request_data.update({
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S')
    })

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == status_code

    if status_code == 200:
        assert all([
            error_field is None,
            error_code is None
        ])

        assert response.data.get('payment_required') is not None

        assert Cart.objects.count() == 0   # cart deleted

    else:
        errors = response.data.get(error_field, [])
        assert len(errors) == 1
        error = errors[0]
        assert error.get('code') == error_code


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize(
    'request_data,status_code,error_fields,error_codes',
    COURIER_DELIVERY_TEST_PARAMETERS
)
def test_create_delivery_order(client, create_cart, create_menu_item, mocker, request_data, status_code, error_fields,
                               error_codes):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == status_code

    if status_code == 200:
        assert all([
            error_fields is None,
            error_codes is None
        ])

        assert response.data.get('payment_required') is not None

        assert Cart.objects.count() == 0  # cart deleted

    else:
        errors = response.data

        assert len(errors) == len(error_fields)

        for error_field, error_code in zip(error_fields, error_codes):
            field_errors = errors.get(error_field)

            assert len(field_errors) == 1
            assert field_errors[0].get('code') == error_code


@pytest.mark.django_db(reset_sequences=True)
def test_create_self_pickup_order_without_self_pickup_time(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        # 'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 400

    errors = response.data.get('self_pickup_time', [])
    assert len(errors) == 1
    error = errors[0]
    assert error.get('code') == 'required'


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_future_self_pickup_time(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    self_pickup_time = dt.datetime.utcnow() + site_settings.min_order_completion_time + dt.timedelta(seconds=1)
    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    order = Order.objects.first()
    assert order.is_payment_required() is False


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_self_pickup_time_too_early(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    self_pickup_time = dt.datetime.utcnow() + dt.timedelta(minutes=10)
    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 400

    errors = response.data.get('self_pickup_time', [])
    assert len(errors) == 1
    error = errors[0]
    assert error.get('code') == 'self_pickup_time_too_early'


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_past_self_pickup_time(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    self_pickup_time = dt.datetime.utcnow() - dt.timedelta(hours=2)
    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 400

    errors = response.data.get('self_pickup_time', [])
    assert len(errors) == 1
    error = errors[0]
    assert error.get('code') == 'self_pickup_time_too_early'


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_without_cart(client):

    site_settings = get_site_settings()

    self_pickup_time = dt.datetime.utcnow() + site_settings.min_order_completion_time + dt.timedelta(seconds=1)
    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 400
    error = response.data.get('detail')
    assert error
    assert error.get('code') == 'cart_not_found'


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_with_empty_cart(client, create_cart):
    session = client.session

    cart = create_cart(session.session_key)

    site_settings = get_site_settings()

    self_pickup_time = dt.datetime.utcnow() + site_settings.min_order_completion_time + dt.timedelta(seconds=1)
    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 400
    error = response.data.get('detail')
    assert error
    assert error.get('code') == 'cart_empty'


@pytest.mark.django_db(reset_sequences=True)
def test_first_customer_order(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Customer.objects.count() == 1

    assert Order.objects.first().customer_id == Customer.objects.first().id


@pytest.mark.django_db(reset_sequences=True)
def test_second_customer_order(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Customer.objects.count() == 1

    assert Order.objects.last().customer_id == Customer.objects.first().id


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_process(client, create_cart, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert DeliveryAddress.objects.count() == 0
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0
    assert OrderTransaction.objects.count() == 0

    for order_item in OrderItem.objects.all():
        if order_item.menu_item.id == menu_item1.id:
            assert order_item.addition_items.count() == 2


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_prepayment_with_card_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                   mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required
    assert DeliveryAddress.objects.count() == 0
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.amount == round(sum([
        menu_item1.price + 2,
        menu_item2.price
    ]) * site_settings.prepayment_percent / 100)

    assert transaction.type == OrderTransactionTypes.PREPAYMENT

    # new order notification will be sent after prepayment confirmed
    assert len(mail.outbox) == 0


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_prepayment_with_cash_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                   mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CASH,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required
    assert DeliveryAddress.objects.count() == 0
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.amount == round(sum([
        menu_item1.price + 2,
        menu_item2.price
    ]) * site_settings.prepayment_percent / 100)

    assert transaction.type == OrderTransactionTypes.PREPAYMENT

    # new order notification will be sent after prepayment confirmed
    assert len(mail.outbox) == 0


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_payment_with_liqpay_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                  mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.LIQPAY,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required is False
    assert DeliveryAddress.objects.count() == 0
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.amount == sum([
        menu_item1.price + 2,
        menu_item2.price
    ])
    assert transaction.amount == Order.objects.first().total_amount

    assert transaction.type == OrderTransactionTypes.FULL_PAYMENT

    # new order notification will be sent after prepayment confirmed
    assert len(mail.outbox) == 0


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_prepayment_with_card_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                   mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('200')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.COURIER,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'settlement': 'Test settlement',
        'street': 'Test street',
        'building_number': '1',
        'apartment_number': '123',
        'entrance_number': '1',
        'floor_number': '1',
        'door_phone_number': '123',
        'peoples_count': 3,
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required
    assert DeliveryAddress.objects.count() == 1
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 0

    # new order notification
    assert len(mail.outbox) == 1


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_prepayment_with_card_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                   mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.COURIER,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'settlement': 'Test settlement',
        'street': 'Test street',
        'building_number': '1',
        'apartment_number': '123',
        'entrance_number': '1',
        'floor_number': '1',
        'door_phone_number': '123',
        'peoples_count': 3,
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required
    assert DeliveryAddress.objects.count() == 1
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.amount == round(sum([
        menu_item1.price + 2,
        menu_item2.price
    ]) * site_settings.prepayment_percent / 100)

    assert transaction.type == OrderTransactionTypes.PREPAYMENT

    # new order notification will be sent after prepayment confirmed
    assert len(mail.outbox) == 0


@pytest.mark.django_db(reset_sequences=True)
def test_create_order_prepayment_with_cash_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                   mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.COURIER,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CASH,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'settlement': 'Test settlement',
        'street': 'Test street',
        'building_number': '1',
        'apartment_number': '123',
        'entrance_number': '1',
        'floor_number': '1',
        'door_phone_number': '123',
        'peoples_count': 3,
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required
    assert DeliveryAddress.objects.count() == 1
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.amount == round(sum([
        menu_item1.price + 2,
        menu_item2.price
    ]) * site_settings.prepayment_percent / 100)

    assert transaction.type == OrderTransactionTypes.PREPAYMENT

    # new order notification will be sent after prepayment confirmed
    assert len(mail.outbox) == 0


@pytest.mark.django_db(reset_sequences=True)
def test_create_delivery_order_payment_with_liqpay_payment(client, create_cart, create_menu_item,
                                                           create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.COURIER,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.LIQPAY,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'settlement': 'Test settlement',
        'street': 'Test street',
        'building_number': '1',
        'apartment_number': '123',
        'entrance_number': '1',
        'floor_number': '1',
        'door_phone_number': '123',
        'peoples_count': 3,
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert Order.objects.count() == 1
    assert Order.objects.first().prepayment_required is False
    assert DeliveryAddress.objects.count() == 1
    assert OrderItem.objects.count() == 2
    assert AdditionItem.objects.count() == 2
    assert Cart.objects.count() == 0

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.amount == sum([
        menu_item1.price + 2,
        menu_item2.price
    ])
    assert transaction.amount == Order.objects.first().total_amount

    assert transaction.type == OrderTransactionTypes.FULL_PAYMENT


@pytest.mark.django_db(reset_sequences=True)
def test_new_order_notification(client, create_menu_item, create_cart, admin_user, create_user, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    site_settings = get_site_settings()
    site_settings.notify_users.add(admin_user)
    site_settings.save()

    self_pickup_time = dt.datetime.utcnow() + site_settings.min_order_completion_time + dt.timedelta(seconds=1)
    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': self_pickup_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert len(mail.outbox) == 1


@pytest.mark.django_db(reset_sequences=True)
def test_new_order_notification_with_prepayment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                mocker, admin_user):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.notify_users.add(admin_user)
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.CARD,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.type == OrderTransactionTypes.PREPAYMENT

    assert len(mail.outbox) == 0


@pytest.mark.django_db(reset_sequences=True)
def test_new_order_notification_with_full_payment(client, create_cart, create_menu_item, create_menu_item_addition,
                                                  mocker, admin_user):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    create_menu_item_addition()
    create_menu_item_addition()

    cart = create_cart(session.session_key)

    add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    site_settings = get_site_settings()
    site_settings.notify_users.add(admin_user)
    site_settings.order_prepayment_start_from = Decimal('20')
    site_settings.save()

    request_data = {
        'delivery_method': DeliveryMethods.SELF_PICKUP,
        'self_pickup_time': get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1),
        'payment_method': PaymentMethods.LIQPAY,
        'customer_name': 'Test',
        'phone_number': '+380000000000',
        'customer_comment': 'Test comment',
    }

    response = client.post(reverse('order_api:create_order'), request_data, content_type='application/json')

    assert response.status_code == 200

    assert OrderTransaction.objects.count() == 1
    transaction = OrderTransaction.objects.first()

    assert transaction.type == OrderTransactionTypes.FULL_PAYMENT

    assert len(mail.outbox) == 0
