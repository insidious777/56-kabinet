import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

from menu.models import Addition
from menu.views import AdditionsListView
from order.repository.cart import add_menu_item_to_cart


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_view_status_code(client):
    response = client.get(reverse('menu:additions_list'))
    assert response.status_code == 200


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_view_status_code_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('menu:additions_list'))
    assert response.status_code == 200


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_view_payment_redirect(client, create_order, create_cart, create_menu_item, mocker):
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

    response = client.get(reverse('menu:additions_list'))

    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_view_context(rf, create_menu_item_addition):
    create_menu_item_addition()
    create_menu_item_addition()
    create_menu_item_addition(show=False)

    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = AdditionsListView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert len(context.get('additions')) == 2
