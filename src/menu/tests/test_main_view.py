from decimal import Decimal

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

from menu.models import Addition
from menu.views import MainView
from order.repository.cart import add_menu_item_to_cart
from order.repository.order import mark_order_transaction_as_paid


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_status_code(client):
    response = client.get(reverse('menu:main'))

    assert response.status_code == 200


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_status_code_for_authenticated_users(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('menu:additions_list'))
    assert response.status_code == 200


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_payment_redirect(client, create_order, create_cart, create_menu_item, mocker):
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

    response = client.get(reverse('menu:main'))

    assert response.status_code == 302


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_not_redirecting_when_payment_paid(client, create_order, create_cart, create_menu_item, mocker):
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
    mark_order_transaction_as_paid(order.transaction)

    response = client.get(reverse('menu:main'))

    assert response.status_code == 200


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_menu_categories(rf, create_menu_category, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    category1 = create_menu_category()
    category2 = create_menu_category()
    create_menu_item(category=category1)
    create_menu_item(category=category2)

    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert len(context.get(view.context_object_name)) == 2


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_menu_categories_ordering(rf, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    create_menu_item()

    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert context.get(view.context_object_name).query.order_by == ('order_index',)


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_menu_categories_filtering(rf, create_menu_category, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    category1 = create_menu_category()
    category2 = create_menu_category()
    create_menu_item(category=category1)
    create_menu_item(category=category2)

    request = rf.get(reverse('menu:main') + '?category_id=1')
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert len(context.get(view.context_object_name)) == 1


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_menu_categories_filtering_by_invalid_value(rf, create_menu_category, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    category1 = create_menu_category()
    category2 = create_menu_category()
    create_menu_item(category=category1)
    create_menu_item(category=category2)

    request = rf.get(reverse('menu:main') + '?category_id=invalid')
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert len(context.get(view.context_object_name)) == 2


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_actions_for_unauthenticated_users(rf):

    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert context.get('actions') is not None


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_actions_for_authenticated_users(rf, create_user):

    user = create_user(is_staff=True, is_superuser=True)

    request = rf.get(reverse('menu:main'))
    request.user = user

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert context.get('actions') is None


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_menu_items_in_cart(rf, create_menu_item, create_cart, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    menu_item1 = create_menu_item(price=10)
    menu_item2 = create_menu_item(price=20)

    cart = create_cart(request.session.session_key)

    cart_item1 = add_menu_item_to_cart(cart, menu_item1, Addition.objects.none(), 1)
    cart_item1.count = 2
    cart_item1.save()

    add_menu_item_to_cart(cart, menu_item2, Addition.objects.none(), 1)

    cart.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert context.get('menu_items_in_cart') == {menu_item1.id, menu_item2.id}
    assert context.get('total_amount') == Decimal((cart_item1.menu_item.price * cart_item1.count) + menu_item2.price)


@pytest.mark.django_db(reset_sequences=True)
def test_main_view_menu_items_in_cart_empty(rf):
    request = rf.get(reverse('menu:main'))
    request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert context.get('menu_items_in_cart') == set()
    assert context.get('total_amount') is None


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

    view = MainView()
    view.setup(request)

    context = view.get_context_data(object_list=view.get_queryset())

    assert len(context.get('additions')) == 2
