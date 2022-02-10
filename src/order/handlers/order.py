import logging
from smtplib import SMTPException

from django.template import loader

from common.utils import send_email
from fs_cabinet.settings import DEFAULT_LOGGER_NAME
from order.constants import DeliveryMethods
from settings.repository import get_site_settings

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


def render_email(subject_template_name, email_template_name, context, html_email_template_name=None):
    subject = loader.render_to_string(subject_template_name, context)
    subject = ''.join(subject.splitlines())     # Email subject *must not* contain newlines

    message = loader.render_to_string(email_template_name, context)

    html_message = None

    if html_email_template_name is not None:
        html_message = loader.render_to_string(html_email_template_name, context)

    return subject, message, html_message


def render_email_for_new_order_notification(order):
    is_payment_required = order.is_payment_required()

    delivery_address = None
    if order.delivery_method == DeliveryMethods.COURIER:
        delivery_address = order.delivery_address

    context = {
        'order_id': order.id,
        'total_amount': order.total_amount,
        'order_items': order.items.all(),
        'customer_name': order.customer.name,
        'customer_phone_number': order.customer.phone_number,
        'delivery_method': order.get_delivery_method_display(),
        'self_pickup_time': order.self_pickup_time,
        'payment_method': order.get_payment_method_display(),
        'payment_required': is_payment_required,
        'peoples_count': order.peoples_count,
        'customer_comment': order.customer_comment,
        'delivery_address': delivery_address,
    }

    if is_payment_required:
        context.update({
            'payment_type': order.transaction.get_type_display(),
            'payment_amount': order.transaction.amount,
            'payment_status': order.transaction.get_status_display()
        })

    return render_email(
        'notifications/new_order/subject.txt',
        email_template_name='notifications/new_order/new_order.html',
        html_email_template_name='notifications/new_order/new_order_html.html',
        context=context,
    )


def send_new_order_notification(order):
    rendered_subject, rendered_message, rendered_html_message = render_email_for_new_order_notification(order)

    site_settings = get_site_settings()
    emails = [user.email for user in site_settings.notify_users.filter(is_active=True)]

    try:
        send_email(
            rendered_subject,
            emails,
            rendered_message,
            rendered_html_message,
        )

    except SMTPException as e:
        logger.error(f'Unable to send new order notification, error: {e}')
