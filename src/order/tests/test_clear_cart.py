import pytest
from django.urls import reverse

from menu.models import Addition
from order.repository.cart import add_menu_item_to_cart


@pytest.mark.django_db(reset_sequences=True)
def test_clear_cart(client, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session
    cart = create_cart(session.session_key)
    menu_item = create_menu_item(price=10)
    add_menu_item_to_cart(cart, menu_item, Addition.objects.none(), 1)
    cart.save()

    response = client.post(reverse('order_api:clear_cart'))

    assert response.status_code == 200

    cart.refresh_from_db()
    assert cart.items.count() == 0
    assert cart.total_amount == 0


@pytest.mark.django_db(reset_sequences=True)
def test_clear_not_existing_cart(client):
    response = client.post(reverse('order_api:clear_cart'))
    assert response.status_code == 404
