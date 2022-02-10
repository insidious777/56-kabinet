import datetime as dt
import re
from decimal import Decimal

import pytest

from menu.models import Addition
from order.constants import DeliveryMethods
from order.handlers.order import render_email_for_new_order_notification
from order.repository.cart import add_menu_item_to_cart
from settings.repository import get_site_settings


@pytest.mark.django_db(reset_sequences=True)
def test_new_self_pickup_order_notification_render(client, create_menu_item, create_cart, create_menu_item_addition, create_order, mocker):
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

    self_pickup_time = dt.datetime(year=2021, month=11, day=1, hour=20, minute=0)
    order = create_order(
        session.session_key,
        cart,
        delivery_method=DeliveryMethods.SELF_PICKUP,
        peoples_count=3,
        customer_comment='test',
        self_pickup_time=self_pickup_time,
    )

    rendered_subject, rendered_message, rendered_html_message = render_email_for_new_order_notification(order)

    print('rendered_message', rendered_html_message)

    assert f'Нове замовлення {order.id}! Загальна сума: {order.total_amount} грн'

    for message in (rendered_message, rendered_html_message):
        assert re.search(f'Замовлення ID {order.id}', message, flags=re.DOTALL)

        for item in order.items.all():
            pattern = f'{item.title}.*? - {item.count} шт.'
            assert re.search(pattern, message, flags=re.DOTALL)

            for addition in item.addition_items.all():
                pattern = f'(<li>)?{addition.title}'
                assert re.search(pattern, message, flags=re.DOTALL)

        assert f'Загальна сума: {order.total_amount}' in message

        assert f'Ім\'я: {order.customer.name}' in message
        assert f'Телефон: {order.customer.phone_number}' in message
        assert f'Спосіб доставки: {order.get_delivery_method_display()}' in message

        assert 'Час самовивозу: 01 листопада 2021 р. 20:00' in message

        assert f'Спосіб оплати: {order.get_payment_method_display()}' in message

        assert 'Тип оплати' not in message

        assert 'Населений пункт' not in message

        assert f'Кількість осіб: {order.peoples_count}' in message
        assert f'Коментар: {order.customer_comment}'


@pytest.mark.django_db(reset_sequences=True)
def test_new_order_notification_render_with_payment(client, create_menu_item, create_cart, create_menu_item_addition, create_order, mocker):
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

    self_pickup_time = dt.datetime(year=2021, month=11, day=1, hour=20, minute=0)
    order = create_order(
        session.session_key,
        cart,
        delivery_method=DeliveryMethods.SELF_PICKUP,
        peoples_count=3,
        customer_comment='test',
        self_pickup_time=self_pickup_time,
    )

    rendered_subject, rendered_message, rendered_html_message = render_email_for_new_order_notification(order)

    print('rendered_message', rendered_html_message)

    assert f'Нове замовлення {order.id}! Загальна сума: {order.total_amount} грн'

    for message in (rendered_message, rendered_html_message):
        assert re.search(f'Замовлення ID {order.id}', message, flags=re.DOTALL)

        for item in order.items.all():
            pattern = f'{item.title}.*? - {item.count} шт.'
            assert re.search(pattern, message, flags=re.DOTALL)

            for addition in item.addition_items.all():
                pattern = f'(<li>)?{addition.title}'
                assert re.search(pattern, message, flags=re.DOTALL)

        assert f'Загальна сума: {order.total_amount}' in message

        assert f'Ім\'я: {order.customer.name}' in message
        assert f'Телефон: {order.customer.phone_number}' in message
        assert f'Спосіб доставки: {order.get_delivery_method_display()}' in message

        assert 'Час самовивозу: 01 листопада 2021 р. 20:00' in message

        assert f'Спосіб оплати: {order.get_payment_method_display()}' in message

        assert f'Тип оплати: {order.transaction.get_type_display()}' in message
        assert f'Розмір оплати: {order.transaction.amount}' in message
        assert f'Статус оплати: {order.transaction.get_status_display()}' in message

        assert 'Населений пункт' not in message

        assert f'Кількість осіб: {order.peoples_count}' in message
        assert f'Коментар: {order.customer_comment}'


@pytest.mark.django_db(reset_sequences=True)
def test_new_courier_order_notification_render(client, create_menu_item, create_cart, create_menu_item_addition, create_order, mocker):
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

    self_pickup_time = dt.datetime(year=2021, month=11, day=1, hour=20, minute=0)
    order = create_order(
        session.session_key,
        cart,
        delivery_method=DeliveryMethods.COURIER,
        peoples_count=3,
        customer_comment='test',
        self_pickup_time=self_pickup_time,
    )

    rendered_subject, rendered_message, rendered_html_message = render_email_for_new_order_notification(order)

    print('rendered_message', rendered_html_message)

    assert f'Нове замовлення {order.id}! Загальна сума: {order.total_amount} грн'

    for message in (rendered_message, rendered_html_message):
        assert re.search(f'Замовлення ID {order.id}', message, flags=re.DOTALL)

        for item in order.items.all():
            pattern = f'{item.title}.*? - {item.count} шт.'
            assert re.search(pattern, message, flags=re.DOTALL)

            for addition in item.addition_items.all():
                pattern = f'(<li>)?{addition.title}'
                assert re.search(pattern, message, flags=re.DOTALL)

        assert f'Загальна сума: {order.total_amount}' in message

        assert f'Ім\'я: {order.customer.name}' in message
        assert f'Телефон: {order.customer.phone_number}' in message
        assert 'Спосіб доставки: Кур&#x27;єр' in message

        assert 'Час самовивозу: 01 листопада 2021 р. 20:00' in message

        assert f'Спосіб оплати: {order.get_payment_method_display()}' in message

        assert 'Тип оплати' not in message

        assert f'Населений пункт: {order.delivery_address.settlement}' in message
        assert f'Вулиця: {order.delivery_address.street}' in message
        assert f'Номер будинку: {order.delivery_address.building_number}' in message
        assert f'Номер квартири: {order.delivery_address.apartment_number}' in message
        assert f'Номер під\'їзду: {order.delivery_address.entrance_number}' in message
        assert f'Поверх: {order.delivery_address.floor_number}' in message
        assert f'Домофон: {order.delivery_address.door_phone_number}' in message

        assert f'Кількість осіб: {order.peoples_count}' in message
        assert f'Коментар: {order.customer_comment}'
