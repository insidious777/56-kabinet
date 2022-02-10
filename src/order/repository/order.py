from django.db import transaction

from order.constants import PaymentMethods, OrderTransactionTypes, DeliveryMethods, OrderTransactionStatuses
from order.models import Order, OrderItem, DeliveryAddress, OrderTransaction, AdditionItem
from order.repository.customer import get_or_create_customer
from settings.repository import get_site_settings


def create_order_from_cart(session_key, cart, customer, delivery_method, payment_method, peoples_count=None,
                           customer_comment=None, self_pickup_time=None, site_settings=None):
    site_settings = site_settings or get_site_settings()
    prepayment_required = False

    if (
            payment_method in [PaymentMethods.CASH, PaymentMethods.CARD]
            and
            cart.total_amount >= site_settings.order_prepayment_start_from
    ):
        prepayment_required = True

    return Order.objects.create(
        session_key=session_key,
        customer=customer,
        delivery_method=delivery_method,
        self_pickup_time=self_pickup_time,
        peoples_count=peoples_count,
        customer_comment=customer_comment,
        payment_method=payment_method,
        prepayment_required=prepayment_required
    )


def create_order_items_from_cart(cart, order):

    for cart_item in cart.items.all():
        order_item = OrderItem(
            order=order,
            menu_item=cart_item.menu_item,
            title=cart_item.menu_item.title,
            price=cart_item.menu_item.price,
            volume=cart_item.menu_item.volume,
            count=cart_item.count
        )
        order_item.save()

        for addition in cart_item.additions.all():
            addition_item = AdditionItem(
                order_item=order_item,
                addition=addition,
                title=addition.title,
                price=addition.price
            )
            addition_item.save()


def create_delivery_address_for_order(order, settlement, street, building_number, apartment_number=None,
                                      entrance_number=None, floor_number=None, door_phone_number=None):
    return DeliveryAddress.objects.create(
        order=order,
        settlement=settlement,
        street=street,
        building_number=building_number,
        apartment_number=apartment_number,
        entrance_number=entrance_number,
        floor_number=floor_number,
        door_phone_number=door_phone_number
    )


def create_order_transaction(order, site_settings=None):
    site_settings = site_settings or get_site_settings()

    payment_type = OrderTransactionTypes.PREPAYMENT
    amount = round(order.total_amount * site_settings.prepayment_percent / 100)

    if order.payment_method in [PaymentMethods.LIQPAY]:
        payment_type = OrderTransactionTypes.FULL_PAYMENT
        amount = order.total_amount

    return OrderTransaction.objects.create(
        order=order,
        type=payment_type,
        amount=amount
    )


def create_order_process(session_key, cart, customer_name, phone_number, delivery_method, payment_method, settlement=None,
                         street=None, building_number=None, apartment_number=None, entrance_number=None, floor_number=None,
                         door_phone_number=None, peoples_count=None, customer_comment=None, self_pickup_time=None):
    site_settings = get_site_settings()

    with transaction.atomic():
        customer, created = get_or_create_customer(customer_name, phone_number)

        order = create_order_from_cart(session_key, cart, customer, delivery_method, payment_method,
                                       peoples_count=peoples_count, customer_comment=customer_comment,
                                       self_pickup_time=self_pickup_time, site_settings=site_settings)

        create_order_items_from_cart(cart, order)

        if delivery_method == DeliveryMethods.COURIER:
            create_delivery_address_for_order(order, settlement, street, building_number, apartment_number=apartment_number,
                                              entrance_number=entrance_number, floor_number=floor_number,
                                              door_phone_number=door_phone_number)

        if order.is_payment_required():
            create_order_transaction(order, site_settings=site_settings)

        cart.delete()

    return order


def get_order_by_session_key(session_key):
    return Order.objects.filter(session_key=session_key, is_rejected=False).order_by('created_at').last()


def get_order_by_id(order_id):
    return Order.objects.filter(id=order_id).first()


def reject_order(order):
    order.is_rejected = True
    order.save()


def get_order_transaction_by_session_key(session_key):
    return OrderTransaction.objects.filter(order__session_key=session_key, order__is_rejected=False).order_by('order__created_at').last()


def get_order_transaction_by_order_id(order_id):
    return OrderTransaction.objects.filter(order_id=order_id).first()


def add_order_transaction_additional_data(order_transaction, data):
    order_transaction.additional_data = data
    order_transaction.save()


def mark_order_transaction_as_paid(order_transaction):
    order_transaction.status = OrderTransactionStatuses.PAID
    order_transaction.save()
