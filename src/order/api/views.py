import json
import logging

from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.decorators import forbidden_for_authenticated
from common.errors import APIException
from common.utils import decode_base64_string, get_utc_now
from fs_cabinet.settings import DEFAULT_LOGGER_NAME
from menu.repository.menu_item import get_menu_item_by_id, get_menu_item_additions_by_ids
from order.api.serializers import AddToCartRequestSerializer, IncreaseCartItemCountRequestSerializer, \
    CreateOrderRequestSerializer, RemoveCartItemRequestSerializer, DecreaseCartItemCountRequestSerializer, \
    RemoveAdditionFromCartItemRequestSerializer, ConfirmLiqPayPaymentRequestSerilizer
from order.handlers.liqpay import verify_liqpay_signature
from order.handlers.order import send_new_order_notification
from order.repository.cart import get_or_create_cart, add_menu_item_to_cart, get_cart_item_by_id, get_cart, \
    get_cart_item_addition_by_id, cart_items_count
from order.repository.order import create_order_process, reject_order, get_order_transaction_by_session_key, \
    get_order_by_id, get_order_transaction_by_order_id, mark_order_transaction_as_paid, \
    add_order_transaction_additional_data

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


@method_decorator(forbidden_for_authenticated, name='post')
class AddToCart(APIView):

    def post(self, request):
        serializer = AddToCartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_item_id = serializer.validated_data.get('menu_item_id')
        addition_ids = serializer.validated_data.get('addition_ids')
        count = serializer.validated_data.get('count')

        menu_item = serializer.context.get('menu_item') or get_menu_item_by_id(menu_item_id)

        if menu_item is None:
            raise Http404()

        if not menu_item.category.can_order:
            raise APIException(code='menu_item_order_not_allowed')

        if not menu_item.category.can_order_now():
            raise APIException(code='menu_item_order_not_allowed_at_this_time')

        session_key = request.session.session_key

        with transaction.atomic():
            cart, created = get_or_create_cart(session_key)
            additions = get_menu_item_additions_by_ids(menu_item, addition_ids)
            add_menu_item_to_cart(cart, menu_item, additions, count)

        return Response({
            'total_amount': cart.total_amount,
        })


@method_decorator(forbidden_for_authenticated, name='post')
class IncreaseCartItemCount(APIView):

    def post(self, request):
        cart = get_cart(request.session.session_key)

        if cart is None:
            raise Http404()

        serializer = IncreaseCartItemCountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item_id = serializer.validated_data.get('cart_item_id')
        cart_item = get_cart_item_by_id(cart.id, cart_item_id)

        if cart_item is None:
            raise Http404()

        cart_item.count = F('count') + 1
        cart_item.save()
        cart_item.refresh_from_db()

        return Response({
            'count': cart_item.count,
            'cart_item_total_amount': cart_item.total_amount,
            'total_amount': cart_item.cart.total_amount,
        })


@method_decorator(forbidden_for_authenticated, name='post')
class DecreaseCartItemCount(APIView):

    def post(self, request):
        cart = get_cart(request.session.session_key)

        if cart is None:
            raise Http404()

        serializer = DecreaseCartItemCountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item_id = serializer.validated_data.get('cart_item_id')
        cart_item = get_cart_item_by_id(cart.id, cart_item_id)

        if cart_item is None:
            raise Http404()

        if cart_item.count != 1:
            cart_item.count = F('count') - 1
            cart_item.save()
            cart_item.refresh_from_db()

        return Response({
            'count': cart_item.count,
            'cart_item_total_amount': cart_item.total_amount,
            'total_amount': cart_item.cart.total_amount,
        })


@method_decorator(forbidden_for_authenticated, name='post')
class CreateOrderAPIView(APIView):

    def post(self, request):
        session_key = request.session.session_key

        cart = get_cart(session_key)

        if cart is None:
            raise APIException(code='cart_not_found')

        if cart_items_count(cart) == 0:
            raise APIException(code='cart_empty')

        serializer = CreateOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = {
            'cart': cart,
            'session_key': session_key,
            **serializer.validated_data
        }

        order = create_order_process(**validated_data)

        if not order.is_payment_required():
            send_new_order_notification(order)

        return Response({
            'payment_required': order.is_payment_required()
        })


@method_decorator(forbidden_for_authenticated, name='post')
class ClearCartAPIView(APIView):

    def post(self, request):
        cart = get_cart(request.session.session_key)

        if cart is None:
            raise Http404()

        cart.clear()
        cart.save()

        return Response({'status': 'OK'})


@method_decorator(forbidden_for_authenticated, name='post')
class RemoveCartItemFromCartAPIView(APIView):

    def post(self, request):
        cart = get_cart(request.session.session_key)

        if cart is None:
            raise Http404()

        serializer = RemoveCartItemRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item_id = serializer.validated_data.get('cart_item_id')
        cart_item = get_cart_item_by_id(cart.id, cart_item_id)

        if cart_item is None:
            raise Http404()

        cart_item.delete()

        return Response({
            'total_amount': cart_item.cart.total_amount
        })


@method_decorator(forbidden_for_authenticated, name='post')
class RemoveAdditionFromCartItemAPIView(APIView):

    def post(self, request):
        cart = get_cart(request.session.session_key)

        if cart is None:
            raise Http404()

        serializer = RemoveAdditionFromCartItemRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item_id = serializer.validated_data.get('cart_item_id')
        cart_item = get_cart_item_by_id(cart.id, cart_item_id)

        if cart_item is None:
            raise Http404()

        addition_id = serializer.validated_data.get('addition_id')
        addition = get_cart_item_addition_by_id(cart_item, addition_id)

        if addition is None:
            raise Http404()

        cart_item.additions.remove(addition)

        return Response({
            'cart_item_total_amount': cart_item.total_amount,
            'total_amount': cart.total_amount,
        })


@method_decorator(forbidden_for_authenticated, name='post')
class RejectOrderAPIView(APIView):

    def post(self, request):
        order_transaction = get_order_transaction_by_session_key(request.session.session_key)

        if order_transaction is None:
            raise Http404()

        if order_transaction.is_paid():
            raise APIException(code='cannot_be_rejected')

        reject_order(order_transaction.order)
        return Response({'status': 'OK'})


class ConfirmLiqPayPaymentAPIView(APIView):

    def post(self, request):
        serializer = ConfirmLiqPayPaymentRequestSerilizer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.get('data')
        signature = serializer.validated_data.get('signature')

        logger.debug(f'LIQPAY data: {data}')
        logger.debug(f'LIQPAY signature: {signature}')

        is_verified = verify_liqpay_signature(data, signature)

        if not is_verified:
            logger.info(f'Confirm LiqPay payment request verification failed')
            return Response(status=status.HTTP_403_FORBIDDEN)

        json_string = decode_base64_string(data)

        logger.debug(f'LIQPAY json: {json_string}')

        if json_string is None:
            logger.error(f'Received not valid base64 encoded data from LiqPay. Base64 string: {data}')
            raise APIException(code='invalid_base64_string')

        json_data = json.loads(json_string)

        payment_status = json_data.get('status')

        err_code = json_data.get('err_code')
        err_description = json_data.get('err_description')

        order_id = json_data.get('order_id')

        logger.info(f'Received LiqPay callback (order_id: {order_id}) (status: {payment_status}) (err_code: {err_code}) (err_description: {err_description})')

        order = get_order_by_id(order_id)

        if order is None:
            logger.error(f'Order ID {order_id} not found for confirmation')
            raise Http404()

        order_transaction = get_order_transaction_by_order_id(order_id)

        if order_transaction is None:
            logger.error(f'Order ID {order.id} transaction not found for confirmation')
            raise Http404()

        if payment_status != 'success':
            add_order_transaction_additional_data(order_transaction, {
                'status': payment_status,
                'err_code': err_code,
                'err_description': err_description,
                'updated_at': get_utc_now().isoformat(),
            })
            return Response(status=status.HTTP_200_OK)

        with transaction.atomic():
            add_order_transaction_additional_data(order_transaction, {
                'status': payment_status,
                'liqpay_order_id': json_data.get('liqpay_order_id'),
                'payment_id': json_data.get('payment_id'),
                'paytype': json_data.get('paytype'),
                'refund_date_last': json_data.get('refund_date_last'),
                'sender_card_type': json_data.get('sender_card_type'),
                'sender_commission': json_data.get('sender_commission'),
                'sender_first_name': json_data.get('sender_first_name'),
                'sender_last_name': json_data.get('sender_last_name'),
                'sender_phone': json_data.get('sender_phone'),
                'token': json_data.get('token'),
                'type': json_data.get('type'),
                'updated_at': get_utc_now().isoformat(),
            })
            mark_order_transaction_as_paid(order_transaction)

        send_new_order_notification(order)

        return Response(status=status.HTTP_200_OK)
