from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from common.utils import convert_utc_to_local
from menu.repository.menu_item import get_menu_item_by_id
from order.api.validators import positive_small_integer_validator, phone_number_validator, self_pickup_time_validator
from order.constants import DeliveryMethods, PaymentMethods


class AddToCartRequestSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    count = serializers.IntegerField(validators=[positive_small_integer_validator])
    addition_ids = serializers.ListField(
        allow_empty=True,
        child=serializers.IntegerField()
    )

    def validate(self, attrs):
        menu_item_id = attrs.get('menu_item_id')
        menu_item = get_menu_item_by_id(menu_item_id)

        addition_ids = attrs.get('addition_ids')
        if addition_ids:
            if len(set(addition_ids)) != menu_item.possible_additions.filter(id__in=addition_ids).count():
                raise serializers.ValidationError(code='addition_not_allowed')

        self.context['menu_item'] = menu_item
        return attrs


class CartItemIdSerializer(serializers.Serializer):
    cart_item_id = serializers.IntegerField()


class IncreaseCartItemCountRequestSerializer(CartItemIdSerializer):
    pass


class DecreaseCartItemCountRequestSerializer(CartItemIdSerializer):
    pass


class CreateOrderRequestSerializer(serializers.Serializer):
    delivery_method = serializers.ChoiceField(choices=[
        DeliveryMethods.COURIER,
        DeliveryMethods.SELF_PICKUP,
    ])
    self_pickup_time = serializers.DateTimeField(validators=[self_pickup_time_validator], required=False)
    payment_method = serializers.ChoiceField(choices=[
        PaymentMethods.CASH,
        PaymentMethods.CARD,
        PaymentMethods.LIQPAY,
    ])

    customer_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(validators=[phone_number_validator])

    settlement = serializers.CharField(max_length=100, required=False)
    street = serializers.CharField(max_length=100, required=False)
    building_number = serializers.CharField(max_length=15, required=False)

    apartment_number = serializers.CharField(max_length=15, allow_null=True, allow_blank=True, required=False)
    entrance_number = serializers.CharField(max_length=15, allow_null=True, allow_blank=True, required=False)
    floor_number = serializers.CharField(max_length=15, allow_null=True, allow_blank=True, required=False)
    door_phone_number = serializers.CharField(max_length=15, allow_null=True, allow_blank=True, required=False)

    peoples_count = serializers.IntegerField(validators=[positive_small_integer_validator], allow_null=True, required=False)
    customer_comment = serializers.CharField(max_length=255, allow_null=True, allow_blank=True, required=False)

    def validate(self, attrs):
        errors = {}

        if attrs.get('delivery_method') == DeliveryMethods.SELF_PICKUP and attrs.get('self_pickup_time') is None:
            errors['self_pickup_time'] = ErrorDetail(_('This field is required.'), code='required')

        self_pickup_time = attrs.get('self_pickup_time')
        if self_pickup_time:
            self_pickup_time = convert_utc_to_local(self_pickup_time)
            attrs['self_pickup_time'] = self_pickup_time

        if attrs.get('delivery_method') == DeliveryMethods.COURIER:

            if not attrs.get('settlement'):
                errors['settlement'] = ErrorDetail(_('This field is required.'), code='required')

            if not attrs.get('street'):
                errors['street'] = ErrorDetail(_('This field is required.'), code='required')

            if not attrs.get('building_number'):
                errors['building_number'] = ErrorDetail(_('This field is required.'), code='required')

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class RemoveCartItemRequestSerializer(CartItemIdSerializer):
    pass


class RemoveAdditionFromCartItemRequestSerializer(CartItemIdSerializer):
    addition_id = serializers.IntegerField()


class ConfirmLiqPayPaymentRequestSerilizer(serializers.Serializer):
    data = serializers.CharField()
    signature = serializers.CharField()
