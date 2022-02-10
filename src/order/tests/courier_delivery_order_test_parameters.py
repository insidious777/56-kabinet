from copy import deepcopy

from order.constants import DeliveryMethods, PaymentMethods

_VALID_DATA = {
    'delivery_method': DeliveryMethods.COURIER,
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


def remove_fields(fields):
    d = get_valid_data()

    for field in fields:
        del d[field]

    return d


COURIER_DELIVERY_TEST_PARAMETERS = (
    (update_valid_data({
        'settlement': 't' * 101
    }), 400, ['settlement'], ['max_length']),

    (update_valid_data({
        'settlement': 123
    }), 200, None, None),

    (update_valid_data({
        'settlement': ''
    }), 400, ['settlement'], ['blank']),

    (update_valid_data({
        'settlement': None
    }), 400, ['settlement'], ['null']),

    (remove_fields(['settlement']), 400, ['settlement'], ['required']),

    (update_valid_data({
        'street': 't' * 101
    }), 400, ['street'], ['max_length']),

    (update_valid_data({
        'street': 123
    }), 200, None, None),

    (update_valid_data({
        'street': ''
    }), 400, ['street'], ['blank']),

    (update_valid_data({
        'street': None
    }), 400, ['street'], ['null']),

    (remove_fields(['street']), 400, ['street'], ['required']),

    (update_valid_data({
        'building_number': 't' * 16
    }), 400, ['building_number'], ['max_length']),

    (update_valid_data({
        'building_number': 123
    }), 200, None, None),

    (update_valid_data({
        'building_number': ''
    }), 400, ['building_number'], ['blank']),

    (update_valid_data({
        'building_number': None
    }), 400, ['building_number'], ['null']),

    (remove_fields(['building_number']), 400, ['building_number'], ['required']),

    (update_valid_data({
        'apartment_number': 't' * 16
    }), 400, ['apartment_number'], ['max_length']),

    (update_valid_data({
        'apartment_number': 123
    }), 200, None, None),

    (update_valid_data({
        'apartment_number': ''
    }), 200, None, None),

    (update_valid_data({
        'apartment_number': None
    }), 200, None, None),

    (remove_fields(['apartment_number']), 200, None, None),

    (update_valid_data({
        'entrance_number': 't' * 16
    }), 400, ['entrance_number'], ['max_length']),

    (update_valid_data({
        'entrance_number': 123
    }), 200, None, None),

    (update_valid_data({
        'entrance_number': ''
    }), 200, None, None),

    (update_valid_data({
        'entrance_number': None
    }), 200, None, None),

    (remove_fields(['entrance_number']), 200, None, None),

    (update_valid_data({
        'floor_number': 't' * 16
    }), 400, ['floor_number'], ['max_length']),

    (update_valid_data({
        'floor_number': 123
    }), 200, None, None),

    (update_valid_data({
        'floor_number': ''
    }), 200, None, None),

    (update_valid_data({
        'floor_number': None
    }), 200, None, None),

    (remove_fields(['floor_number']), 200, None, None),

    (update_valid_data({
        'door_phone_number': 't' * 16
    }), 400, ['door_phone_number'], ['max_length']),

    (update_valid_data({
        'door_phone_number': 123
    }), 200, None, None),

    (update_valid_data({
        'door_phone_number': ''
    }), 200, None, None),

    (update_valid_data({
        'door_phone_number': None
    }), 200, None, None),

    (remove_fields(['door_phone_number']), 200, None, None),

    (update_valid_data({
        'peoples_count': 32767 + 1
    }), 400, ['peoples_count'], ['peoples_count_range_from_0_to_32767']),

    (update_valid_data({
        'peoples_count': '123'
    }), 200, None, None),

    (update_valid_data({
        'peoples_count': ''
    }), 400, ['peoples_count'], ['invalid']),

    (update_valid_data({
        'peoples_count': None
    }), 200, None, None),

    (remove_fields(['peoples_count']), 200, None, None),

    (
        remove_fields([
            'settlement',
            'street',
            'building_number'
        ]),
        400,
        [
            'settlement',
            'street',
            'building_number'
        ],
        [
            'required',
            'required',
            'required'
        ]
    ),
)
