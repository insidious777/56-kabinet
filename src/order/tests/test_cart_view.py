import datetime as dt

import pytest
from django.urls import reverse

from common.utils import get_local_now
from menu.models import Addition
from order.repository.cart import add_menu_item_to_cart


@pytest.mark.django_db(reset_sequences=True)
def test_cart_view_redirect_if_cart_not_exist(client):
    response = client.get(reverse('order:cart'))
    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_cart_view_redirect_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('order:cart'))
    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_cart_view_payment_redirect(client, create_order, create_cart, create_menu_item, mocker):
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

    create_order(session.session_key, cart)

    response = client.get(reverse('order:cart'))

    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_cart_view_status_code(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session
    cart = create_cart(session.session_key)
    menu_item = create_menu_item(price=10)
    add_menu_item_to_cart(cart, menu_item, Addition.objects.none(), 1)
    cart.save()

    response = client.get(reverse('order:cart'))
    assert response.status_code == 200


@pytest.mark.django_db(reset_sequences=True)
def test_cart_view_excluded_cart_items_by_category_time_restrictions(client, create_cart, create_menu_category, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    now = get_local_now()

    from_time = now - dt.timedelta(hours=6)
    to_time = now - dt.timedelta(hours=3)

    restricted_category = create_menu_category(from_time=from_time, to_time=to_time)
    menu_items_should_be_excluded = [
        create_menu_item(category=restricted_category, price=10),
        create_menu_item(category=restricted_category, price=10),
    ]

    category = create_menu_category()
    menu_items_should_be_kept = [
        create_menu_item(category=category, price=10),
        create_menu_item(category=category, price=10),
    ]

    session = client.session
    cart = create_cart(session.session_key)

    menu_item_addition = create_menu_item_addition()

    for menu_item in menu_items_should_be_excluded:
        add_menu_item_to_cart(cart, menu_item, Addition.objects.filter(id=menu_item_addition.id), 1)

    for menu_item in menu_items_should_be_kept:
        add_menu_item_to_cart(cart, menu_item, Addition.objects.filter(id=menu_item_addition.id), 1)

    cart.save()

    response = client.get(reverse('order:cart'))
    assert response.status_code == 200

    assert {
        *[cart_item.menu_item.id for cart_item in response.context.get('excluded_cart_items', [])]
    } == {
        *[menu_item.id for menu_item in menu_items_should_be_excluded]
    }

    cart.refresh_from_db()
    assert cart.total_amount == sum(menu_item.price for menu_item in menu_items_should_be_kept) + 2     # two additions for price of 1

    # check excluded cart items empty at second visit
    response = client.get(reverse('order:cart'))
    assert response.status_code == 200

    assert response.context.get('excluded_cart_items') == []
