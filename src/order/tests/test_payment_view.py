import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

from menu.models import Addition
from order.constants import OrderTransactionStatuses
from order.repository.cart import add_menu_item_to_cart
from order.views import PaymentView


@pytest.mark.django_db(reset_sequences=True)
def test_payment_view_redirect_when_payment_not_needed(client, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    session = client.session

    menu_item1 = create_menu_item(price=100)
    menu_item2 = create_menu_item(price=75)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    create_order(session.session_key, cart)

    response = client.get(reverse('order:payment'))

    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_payment_view_redirect_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('order:payment'))
    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_payment_view_redirect_when_payment_paid(client, create_order, create_cart, create_menu_item, mocker):
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

    response = client.get(reverse('order:payment'))

    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_payment_view_context(rf, create_order, create_cart, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    session = request.session

    menu_item1 = create_menu_item(price=399)
    menu_item2 = create_menu_item(price=1)

    cart = create_cart(session.session_key)
    add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)
    cart.save()

    order = create_order(session.session_key, cart)

    view = PaymentView()
    view.setup(request)

    view.object = view.get_object()
    context = view.get_context_data()

    order_transaction = context.get(view.context_object_name)
    assert order_transaction.id == order.transaction.id

    payment_form = context.get('payment_form')
    assert payment_form
