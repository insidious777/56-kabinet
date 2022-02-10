from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from order.utils import is_valid_phone_number


def phone_number_validator(phone_number: str):
    if not is_valid_phone_number(phone_number):
        raise ValidationError(_('Phone number has to be in "+380999999999" format'))
