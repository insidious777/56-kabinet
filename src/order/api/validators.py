from rest_framework import serializers

from common.utils import get_local_now, convert_utc_to_local
from order.utils import is_valid_positive_small_integer, is_valid_phone_number
from settings.repository import get_site_settings


def phone_number_validator(phone_number):
    if not is_valid_phone_number(phone_number):
        raise serializers.ValidationError(code='invalid_phone_number_format')


def positive_small_integer_validator(value: int):
    if not is_valid_positive_small_integer(value):
        raise serializers.ValidationError(code='peoples_count_range_from_0_to_32767')


def self_pickup_time_validator(self_pickup_time):

    if convert_utc_to_local(self_pickup_time) < (get_local_now() + get_site_settings().min_order_completion_time):
        raise serializers.ValidationError(code='self_pickup_time_too_early')
