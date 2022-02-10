import datetime as dt

import pytest
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from common.utils import get_local_now
from menu.models import MenuItem, MenuCategory, Addition
from order.constants import DeliveryMethods, PaymentMethods
from order.models import Cart
from order.repository.order import create_order_process
from settings.models import Settings
from settings.repository import get_site_settings


@pytest.fixture(autouse=True)
def create_site_settings(db):
    Settings.objects.get_or_create()


@pytest.fixture
def create_user(db):

    def make_create_user(username='Test', password='testabc123', **kwargs):
        return User.objects.create_user(username=username, password=password, **kwargs)

    return make_create_user


@pytest.fixture
def admin_user(db, create_user):
    return create_user(email='test@gmail.com', is_staff=True, is_superuser=True)


@pytest.fixture
def create_menu_category(db):

    def make_create_menu_category(name='Test', icon=None, **kwargs):
        return MenuCategory.objects.create(
            icon=icon or ContentFile(b''),
            name=name,
            **kwargs
        )

    return make_create_menu_category


@pytest.fixture
def create_menu_item_addition(db):

    def make_create_addition(title='Test', price=1, show=True):
        addition = Addition.objects.create(
            title=title,
            price=price,
            show=show
        )
        return addition

    return make_create_addition


@pytest.fixture
def create_menu_item(db, create_menu_category, create_menu_item_addition):

    def make_create_menu_item(title='Test', price='0', volume='100 г', category=None, additions_count=0, additions=None, **kwargs):
        category = category or create_menu_category()
        menu_item = MenuItem.objects.create(
            title=title,
            price=price,
            volume=volume,
            category=category,
            **kwargs
        )

        for _ in range(additions_count):
            menu_item.possible_additions.add(create_menu_item_addition())

        if additions:
            menu_item.possible_additions.add(*additions)

        return menu_item

    return make_create_menu_item


@pytest.fixture
def create_cart(db):

    def make_create_cart(session_key):
        return Cart.objects.create(session_key=session_key)

    return make_create_cart


@pytest.fixture
def create_order(db):

    def make_create_order(session_key, cart, customer_name='test', phone_number='+380123456789',
                          delivery_method=DeliveryMethods.SELF_PICKUP, payment_method=PaymentMethods.CARD,
                          settlement='test', street='test', building_number='test', apartment_number='test',
                          entrance_number='test', floor_number='test', door_phone_number='123', peoples_count=3,
                          customer_comment='test', self_pickup_time=None):

        if delivery_method == DeliveryMethods.SELF_PICKUP and self_pickup_time is None:
            site_settings = get_site_settings()
            self_pickup_time = get_local_now() + site_settings.min_order_completion_time + dt.timedelta(minutes=1)

        order = create_order_process(session_key, cart, customer_name, phone_number, delivery_method, payment_method,
                                     settlement=settlement, street=street, building_number=building_number,
                                     apartment_number=apartment_number, entrance_number=entrance_number,
                                     floor_number=floor_number, door_phone_number=door_phone_number,
                                     peoples_count=peoples_count, customer_comment=customer_comment,
                                     self_pickup_time=self_pickup_time)
        return order

    return make_create_order
