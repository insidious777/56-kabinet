import base64
import binascii
import datetime as dt

import pytz
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.template import loader


def get_utc_now():
    return dt.datetime.utcnow().replace(tzinfo=pytz.UTC)


def get_local_now():
    local_timezone = pytz.timezone(settings.LOCAL_TIME_ZONE)
    return dt.datetime.now(tz=local_timezone)


def convert_utc_to_local(time):
    time = time.replace(tzinfo=pytz.UTC)
    return time.astimezone(pytz.timezone(settings.LOCAL_TIME_ZONE))


def get_exact_match(model_class, m2m_field, ids):
    query = model_class.objects.annotate(count_objects=Count(m2m_field)).filter(count_objects=len(ids))

    for _id in ids:
        query = query.filter(**{m2m_field: _id})

    return query


def decode_base64_string(b64_string):
    try:
        return base64.b64decode(b64_string).decode('utf-8')
    except binascii.Error:
        return None


def send_email(subject, emails, message, html_message=None):
    email_message = EmailMultiAlternatives(subject, message, settings.EMAIL_SENDER, emails)

    if html_message is not None:
        email_message.attach_alternative(html_message, 'text/html')

    email_message.send()
