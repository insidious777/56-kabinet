import datetime as dt

import pytest
from django.urls import reverse

from common.utils import get_local_now
from order.models import Cart, CartItem


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_forbidden_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('order_api:add_to_cart'))
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_menu_item_from_disabled_order_category(client, create_menu_category, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    category = create_menu_category(can_order=False)
    menu_item = create_menu_item(category=category, price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    error = response.data.get('detail', {})
    assert error.get('code') == 'menu_item_order_not_allowed'

    assert Cart.objects.count() == 0
    assert CartItem.objects.count() == 0


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_menu_item_with_time_restriction(client, create_menu_category, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    now = get_local_now()

    # if you set realistic hours, then test will be time dependant
    # and when plus hours will across 00:00 then test will fail
    from_time = now - dt.timedelta(seconds=6)
    to_time = now - dt.timedelta(seconds=3)

    category = create_menu_category(from_time=from_time, to_time=to_time)
    menu_item = create_menu_item(category=category, price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    error = response.data.get('detail', {})
    assert error.get('code') == 'menu_item_order_not_allowed_at_this_time'

    assert Cart.objects.count() == 0
    assert CartItem.objects.count() == 0


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_menu_item_within_time_restriction(client, create_menu_category, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    now = get_local_now()

    # if you set realistic hours, then test will be time dependant
    # and when plus hours will across 00:00 then test will fail
    from_time = now - dt.timedelta(seconds=3)
    to_time = now + dt.timedelta(seconds=3)

    category = create_menu_category(from_time=from_time, to_time=to_time)
    menu_item = create_menu_item(category=category, price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 200
    assert response.data.get('total_amount') == menu_item.price

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 1

    assert Cart.objects.first().total_amount == menu_item.price


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_menu_item_without_additions(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 200
    assert response.data.get('total_amount') == menu_item.price

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 1

    assert Cart.objects.first().total_amount == menu_item.price


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_menu_item_with_additions(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10, additions_count=5)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [1, 2],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 200
    assert response.data.get('total_amount') == menu_item.price + 2     # two additions for 1 UAH (addition has default price 1 UAH for tests simplification)

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 1

    assert Cart.objects.first().total_amount == menu_item.price + 2


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_same_item_without_additions_twice(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [],
    }


    client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')
    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 200
    assert response.data.get('total_amount') == menu_item.price * 2

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 1

    assert Cart.objects.first().total_amount == menu_item.price * 2


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_same_item_with_additions_twice(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10, additions_count=5)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [1, 2, 3],
    }

    client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')
    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 200
    assert response.data.get('total_amount') == (menu_item.price + 3) * 2

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 1

    assert Cart.objects.first().total_amount == (menu_item.price + 3) * 2


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_same_item_with_different_additions(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10, additions_count=5)

    request_data1 = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [1, 2, 3],
    }

    request_data2 = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': [1, 2],
    }

    client.post(reverse('order_api:add_to_cart'), request_data1, content_type='application/json')
    response = client.post(reverse('order_api:add_to_cart'), request_data2, content_type='application/json')

    assert response.status_code == 200
    assert response.data.get('total_amount') == sum([
        menu_item.price + 3,
        menu_item.price + 2
    ])

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 2

    assert Cart.objects.first().total_amount == sum([
        menu_item.price + 3,
        menu_item.price + 2
    ])


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_two_different_items(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    request_data1 = {
        'menu_item_id': menu_item1.id,
        'count': 1,
        'addition_ids': [],
    }
    request_data2 = {
        'menu_item_id': menu_item2.id,
        'count': 1,
        'addition_ids': [],
    }

    response1 = client.post(reverse('order_api:add_to_cart'), request_data1, content_type='application/json')
    response2 = client.post(reverse('order_api:add_to_cart'), request_data2, content_type='application/json')

    assert response1.status_code == 200
    assert response1.data.get('total_amount') == menu_item1.price

    assert response2.status_code == 200
    assert response2.data.get('total_amount') == sum([menu_item1.price, menu_item2.price])

    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 2

    assert Cart.objects.first().total_amount == sum([menu_item1.price, menu_item2.price])


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_not_existing_item(client, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request_data = {
        'menu_item_id': 666,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 404


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_missed_menu_item(client, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request_data = {
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('menu_item_id')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'required'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_menu_item_as_null(client, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request_data = {
        'menu_item_id': None,
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('menu_item_id')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'null'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_invalid_menu_item(client, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request_data = {
        'menu_item_id': '',
        'count': 1,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('menu_item_id')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'invalid'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_missed_count(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('count')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'required'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_count_as_null(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': None,
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('count')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'null'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_invalid_count(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': '',
        'addition_ids': [],
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('count')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'invalid'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_missed_addition_ids(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('addition_ids')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'required'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_addition_ids_as_null(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': None,
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('addition_ids')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'null'


@pytest.mark.django_db(reset_sequences=True)
def test_add_to_cart_with_invalid_addition_ids(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(price=10)

    request_data = {
        'menu_item_id': menu_item.id,
        'count': 1,
        'addition_ids': '',
    }

    response = client.post(reverse('order_api:add_to_cart'), request_data, content_type='application/json')

    assert response.status_code == 400

    menu_item_id_errors = response.data.get('addition_ids')

    assert len(menu_item_id_errors) == 1
    assert menu_item_id_errors[0].get('code') == 'not_a_list'
