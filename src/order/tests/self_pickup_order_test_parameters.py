from copy import deepcopy

from order.constants import DeliveryMethods, PaymentMethods


_VALID_DATA = {
    'delivery_method': DeliveryMethods.SELF_PICKUP,
    'payment_method': PaymentMethods.CARD,
    'customer_name': 'Test',
    'phone_number': '+380000000000',
    'settlement': 'Test settlement',
    'street': 'Test street',
    'building_number': '1',
    'apartment_number': '123',
    'entrance_number': '1',
    'floor_number': '1',
    'door_phone_number': '123',
    'peoples_count': 3,
    'customer_comment': 'Test comment',
}


def get_valid_data():
    return deepcopy(_VALID_DATA)


def update_valid_data(upd):
    d = get_valid_data()
    d.update(upd)
    return d


def remove_field(field):
    d = get_valid_data()
    del d[field]
    return d


SELF_PICKUP_ORDER_REQUESTS = (
    (_VALID_DATA, 200, None, None),

    (update_valid_data({
        'payment_method': PaymentMethods.CASH
    }), 200, None, None),

    (update_valid_data({
        'payment_method': PaymentMethods.LIQPAY
    }), 200, None, None),

    (update_valid_data({
        'payment_method': 'test'
    }), 400, 'payment_method', 'invalid_choice'),


    (update_valid_data({
        'customer_name': 't'*101
    }), 400, 'customer_name', 'max_length'),

    (update_valid_data({
        'customer_name': 123
    }), 200, None, None),

    (update_valid_data({
        'customer_name': ''
    }), 400, 'customer_name', 'blank'),

    (update_valid_data({
        'customer_name': None
    }), 400, 'customer_name', 'null'),

    (remove_field('customer_name'), 400, 'customer_name', 'required'),


    (update_valid_data({
        'phone_number': ''
    }), 400, 'phone_number', 'blank'),

    (update_valid_data({
        'phone_number': 'test'
    }), 400, 'phone_number', 'invalid_phone_number_format'),

    (update_valid_data({
        'phone_number': 352
    }), 400, 'phone_number', 'invalid_phone_number_format'),

    (update_valid_data({
        'phone_number': None
    }), 400, 'phone_number', 'null'),

    (remove_field('phone_number'), 400, 'phone_number', 'required'),


    (remove_field('settlement'), 200, None, None),
    (remove_field('street'), 200, None, None),
    (remove_field('building_number'), 200, None, None),
    (remove_field('apartment_number'), 200, None, None),
    (remove_field('entrance_number'), 200, None, None),
    (remove_field('floor_number'), 200, None, None),
    (remove_field('door_phone_number'), 200, None, None),
    (remove_field('peoples_count'), 200, None, None),


    (update_valid_data({
        'settlement': 'Test settlement',
        'street': 'Test street',
        'building_number': '1',
        'apartment_number': '123',
        'entrance_number': '1',
        'floor_number': '1',
        'door_phone_number': '123',
        'peoples_count': 3,
    }), 200, None, None),


    (update_valid_data({
        'customer_comment': 't' * 256
    }), 400, 'customer_comment', 'max_length'),

    (update_valid_data({
        'customer_comment': 123
    }), 200, None, None),

    (update_valid_data({
        'customer_comment': ''
    }), 200, None, None),

    (update_valid_data({
        'customer_comment': None
    }), 200, None, None),

    (remove_field('customer_comment'), 200, None, None),
)
