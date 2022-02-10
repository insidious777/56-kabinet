from django.db.models import F

from common.utils import get_exact_match
from order.models import Cart, CartItem


def get_or_create_cart(session_key):
    return Cart.objects.get_or_create(session_key=session_key)


def get_cart(session_key):
    return Cart.objects.filter(session_key=session_key).order_by('created_at').last()


def cart_items_count(cart):
    return cart.items.count()


def add_menu_item_to_cart(cart, menu_item, additions, count):
    cart_item = get_exact_match(CartItem, 'additions', additions.values_list('id', flat=True)).filter(
        cart=cart,
        menu_item=menu_item,
    ).first()

    if cart_item is None:
        cart_item = CartItem.objects.create(
            cart=cart,
            menu_item=menu_item
        )
        cart_item.additions.add(*additions)

    cart_item.count = F('count') + count
    cart_item.save()
    return cart_item


def get_menu_items_in_cart(session_key):
    cart = get_cart(session_key)

    if cart is None:
        return set()

    return set(cart.items.values_list('menu_item_id', flat=True))


def get_cart_total_amount(session_key):
    cart = get_cart(session_key)

    if cart is not None:
        return cart.total_amount


def get_cart_item_by_id(cart_id, cart_item_id):
    return CartItem.objects.filter(cart_id=cart_id, id=cart_item_id).first()


def get_cart_item_addition_by_id(cart_item, addition_id):
    return cart_item.additions.filter(id=addition_id).first()


def exclude_cart_items_from_cart_by_time_restrictions(cart):
    cart_items_to_exclude = []

    for cart_item in cart.items.all():
        category = cart_item.menu_item.category

        if not category.can_order_now():
            cart_items_to_exclude.append(cart_item)

    CartItem.objects.filter(id__in=[cart_item.id for cart_item in cart_items_to_exclude]).delete()

    excluded_cart_items = cart_items_to_exclude
    return excluded_cart_items
