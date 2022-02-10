import datetime as dt

import pytest
from django.urls import reverse

from menu.models import Addition
from order.constants import OrderTransactionStatuses, DeliveryMethods, PaymentMethods
from order.repository.cart import add_menu_item_to_cart
from settings.repository import get_site_settings


@pytest.mark.django_db(reset_sequences=True)
def test_reject_order_forbidden_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('order_api:reject_order'))
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_reject_order(client, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    mocked_icon_url = mocker.patch('django.db.models.fields.files.ImageFieldFile.url')
    mocked_icon_url.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=400)
    menu_item2 = create_menu_item(price=400)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    order = create_order(session.session_key, cart)

    response = client.post(reverse('order_api:reject_order'))

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.is_rejected

    # test main view can be loaded after rejection
    response = client.get(reverse('menu:main'))
    assert response.status_code == 200

    # and payment view isn't available
    response = client.get(reverse('order:payment'))
    assert response.status_code == 302

    # test new order after old order rejected
    request_data = {
        'menu_item_id': menu_item1.id,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')
    assert response.status_code == 200

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


@pytest.mark.django_db(reset_sequences=True)
def test_reject_order_with_paid_transaction(client, create_order, create_cart, create_menu_item, mocker):
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
    order.transaction.status = OrderTransactionStatuses.PAID
    order.transaction.save()

    response = client.post(reverse('order_api:reject_order'))

    assert response.status_code == 400
    assert response.data.get('detail').get('code') == 'cannot_be_rejected'
    assert order.is_rejected is False


@pytest.mark.django_db(reset_sequences=True)
def test_reject_not_existing_order(client):
    response = client.post(reverse('order_api:reject_order'))

    assert response.status_code == 404
