import pytest
from django.urls import reverse

from menu.models import Addition
from order.repository.cart import add_menu_item_to_cart


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_forbidden_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('order_api:remove_cart_item_addition'))
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition(client, create_cart, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    additions = [
        create_menu_item_addition(),
        create_menu_item_addition(),
        create_menu_item_addition(),
    ]

    cart = create_cart(session.session_key)

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart_item1 = add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    cart_item2 = add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    request_data = {
        'cart_item_id': cart_item1.id,
        'addition_id': additions[0].id,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data)

    assert response.status_code == 200

    assert response.data.get('total_amount') == sum([
        menu_item1.price + 2,
        menu_item2.price
    ])

    assert response.data.get('cart_item_total_amount') == menu_item1.price + 2

    cart_item1.refresh_from_db()
    cart_item2.refresh_from_db()

    assert cart_item1.additions.count() == 2
    assert cart_item2.additions.count() == 0

    cart.refresh_from_db()
    assert cart.total_amount == sum([
        menu_item1.price + 2,
        menu_item2.price
    ])


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_from_not_existing_cart(client, create_cart, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    additions = [
        create_menu_item_addition(),
        create_menu_item_addition(),
        create_menu_item_addition(),
    ]

    cart = create_cart('test')

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart_item1 = add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    cart_item2 = add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    request_data = {
        'cart_item_id': cart_item1.id,
        'addition_id': additions[0].id,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data)

    assert response.status_code == 404


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_from_not_existing_cart_item(client, create_cart, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    additions = [
        create_menu_item_addition(),
        create_menu_item_addition(),
        create_menu_item_addition(),
    ]

    cart = create_cart(session.session_key)

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart_item1 = add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    cart_item2 = add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    request_data = {
        'cart_item_id': 666,
        'addition_id': additions[0].id,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data)

    assert response.status_code == 404


@pytest.mark.django_db(reset_sequences=True)
def test_remove_not_existing_cart_item_addition(client, create_cart, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    additions = [
        create_menu_item_addition(),
        create_menu_item_addition(),
        create_menu_item_addition(),
    ]

    cart = create_cart(session.session_key)

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart_item1 = add_menu_item_to_cart(cart, menu_item1, Addition.objects.all(), 1)
    cart_item2 = add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    request_data = {
        'cart_item_id': cart_item1.id,
        'addition_id': 666,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data)

    assert response.status_code == 404


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_with_missed_cart_item_id(client, create_cart):
    session = client.session
    cart = create_cart(session.session_key)

    request_data = {
        # 'cart_item_id': 1,
        'addition_id': 1,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data)

    assert response.status_code == 400
    assert len(response.data) == 1

    errors = response.data.get('cart_item_id')
    assert len(errors) == 1
    assert errors[0].get('code') == 'required'


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_with_missed_addition_id(client, create_cart):
    session = client.session
    cart = create_cart(session.session_key)

    request_data = {
        'cart_item_id': 1,
        # 'addition_id': 1,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data)

    assert response.status_code == 400
    assert len(response.data) == 1

    errors = response.data.get('addition_id')
    assert len(errors) == 1
    assert errors[0].get('code') == 'required'


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_with_null_cart_item_id(client, create_cart):
    session = client.session
    cart = create_cart(session.session_key)

    request_data = {
        'cart_item_id': None,
        'addition_id': 1,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data, content_type='application/json')

    assert response.status_code == 400
    assert len(response.data) == 1

    errors = response.data.get('cart_item_id')
    assert len(errors) == 1
    assert errors[0].get('code') == 'null'


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_with_null_addition_id(client, create_cart):
    session = client.session
    cart = create_cart(session.session_key)

    request_data = {
        'cart_item_id': 1,
        'addition_id': None,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data, content_type='application/json')

    assert response.status_code == 400
    assert len(response.data) == 1

    errors = response.data.get('addition_id')
    assert len(errors) == 1
    assert errors[0].get('code') == 'null'


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_with_invalid_cart_item_id(client, create_cart):
    session = client.session
    cart = create_cart(session.session_key)

    request_data = {
        'cart_item_id': '',
        'addition_id': 1,
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data, content_type='application/json')

    assert response.status_code == 400
    assert len(response.data) == 1

    errors = response.data.get('cart_item_id')
    assert len(errors) == 1
    assert errors[0].get('code') == 'invalid'


@pytest.mark.django_db(reset_sequences=True)
def test_remove_cart_item_addition_with_invalid_addition_id(client, create_cart):
    session = client.session
    cart = create_cart(session.session_key)

    request_data = {
        'cart_item_id': 1,
        'addition_id': '',
    }
    response = client.post(reverse('order_api:remove_cart_item_addition'), request_data, content_type='application/json')

    assert response.status_code == 400
    assert len(response.data) == 1

    errors = response.data.get('addition_id')
    assert len(errors) == 1

    assert errors[0].get('code') == 'invalid'
