import pytest
from django.urls import reverse

from menu.models import Addition
from order.repository.cart import add_menu_item_to_cart


@pytest.mark.django_db(reset_sequences=True)
def test_increase_cart_item_count_forbidden_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('order_api:increase_count'))
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_increase_cart_item_count(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session
    cart = create_cart(session.session_key)
    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)
    cart_item1 = add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    cart_item2 = add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    request_data = {'cart_item_id': cart_item1.id}
    response = client.post(reverse('order_api:increase_count'), request_data)

    assert response.status_code == 200
    assert response.data.get('count') == 2  # 1 was when added to cart by default
    assert response.data.get('cart_item_total_amount') == menu_item1.price * 2
    assert response.data.get('total_amount') == sum([
        menu_item1.price * 2,
        menu_item2.price
    ])


@pytest.mark.django_db(reset_sequences=True)
def test_increase_cart_item_count_in_another_customers_cart(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    cart1 = create_cart(session.session_key)
    cart2 = create_cart('test')

    menu_item = create_menu_item(price=10)

    cart1_item = add_menu_item_to_cart(cart1, menu_item, Addition.objects.none(), 1)
    cart2_item = add_menu_item_to_cart(cart2, menu_item, Addition.objects.none(), 1)

    cart1.save()
    cart2.save()

    request_data = {'cart_item_id': cart2_item.id}
    response = client.post(reverse('order_api:increase_count'), request_data)

    assert response.status_code == 404

    cart2_item.refresh_from_db()
    assert cart2_item.count == 1


@pytest.mark.django_db(reset_sequences=True)
def test_increase_not_existing_cart_item_count(client, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request_data = {'cart_item_id': 666}
    response = client.post(reverse('order_api:increase_count'), request_data)

    assert response.status_code == 404
