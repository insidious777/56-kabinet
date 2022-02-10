import re


def is_valid_phone_number(phone_number: str):
    return bool(re.fullmatch(r'^\+380\d{9}$', phone_number))


def is_valid_positive_small_integer(value: int):
    return 32767 >= value >= 0
