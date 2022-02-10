import datetime as dt
from decimal import Decimal

from django.conf import settings
from django.core.validators import DecimalValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext


class Settings(models.Model):
    min_order_completion_time = models.DurationField(verbose_name=_('Minimum order completion time'), default=dt.timedelta(minutes=30))
    order_prepayment_start_from = models.DecimalField(
        verbose_name=_('Order prepayment start from'),
        max_digits=6,
        decimal_places=0,
        help_text=_('Amount, from which prepayment will be required'),
        default='400',
        validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)]
    )
    prepayment_percent = models.DecimalField(
        verbose_name=_('Prepayment percent'),
        max_digits=6,
        decimal_places=0,
        help_text=_('From total order amount'),
        default='25',
        validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)]
    )

    phone_number = models.CharField(verbose_name=_('Phone number'), max_length=13, default='067 740 00 56')

    instagram_url = models.URLField(verbose_name=_('Instagram URL'), default='https://www.instagram.com/')
    facebook_url = models.URLField(verbose_name=_('Facebook URL'), default='https://www.facebook.com/')

    address = models.CharField(verbose_name=_('Address'), max_length=64, default='м.Тернопіль, вул. Грушевського 1')
    address_url = models.URLField(verbose_name=_('Address URL'), max_length=255, default="https://www.google.com/maps/place/56+%D0%9A%D0%B0%D0%B1%D1%96%D0%BD%D0%B5%D1%82/@49.5539818,25.5927935,18.37z/data=!4m5!3m4!1s0x4730371f9eb9cfbf:0xa6d7469b36e1629c!8m2!3d49.5539927!4d25.593199")

    work_schedule = models.CharField(verbose_name=_('Work schedule'), max_length=100, default='з 8:00 по 22:00')
    work_schedule_on_weekend = models.CharField(verbose_name=_('Work schedule on weekend'), max_length=100, default='з 9:00 по 22:00')

    delivery_available = models.BooleanField(verbose_name=_('Delivery available'), default=False)
    delivery_time_within_city = models.DurationField(verbose_name=_('Delivery time within city'), default=dt.timedelta(minutes=30))
    delivery_time_beyond_city = models.DurationField(verbose_name=_('Delivery time beyond city'), default=dt.timedelta(minutes=60))
    delivery_cost = models.DecimalField(
        verbose_name=_('Delivery cost'),
        max_digits=6,
        decimal_places=0,
        default='30',
        validators=[MinValueValidator(Decimal('0.00')), DecimalValidator(max_digits=6, decimal_places=0)]
    )

    notify_users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Notify users'), help_text=_("Hold down \"Control\", or \"Command\" on a Mac, to select more than one.\nUsers that will receive new order notifications.\nNote: users must have email filled in their profile"))

    class Meta:
        verbose_name = _('Settings')
        verbose_name_plural = _('Settings')

    def __str__(self):
        return gettext('Settings')
