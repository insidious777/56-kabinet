from django.urls import path

from order.api.views import AddToCart, IncreaseCartItemCount, DecreaseCartItemCount, ClearCartAPIView, \
    RemoveCartItemFromCartAPIView, RemoveAdditionFromCartItemAPIView, CreateOrderAPIView, RejectOrderAPIView, \
    ConfirmLiqPayPaymentAPIView

urlpatterns = [
    path('add-to-cart/', AddToCart.as_view(), name='add_to_cart'),
    path('increase-count/', IncreaseCartItemCount.as_view(), name='increase_count'),
    path('decrease-count/', DecreaseCartItemCount.as_view(), name='decrease_count'),
    path('create/', CreateOrderAPIView.as_view(), name='create_order'),
    path('clear/', ClearCartAPIView.as_view(), name='clear_cart'),
    path('remove-cart-item/', RemoveCartItemFromCartAPIView.as_view(), name='remove_cart_item'),
    path('remove-cart-item-addition/', RemoveAdditionFromCartItemAPIView.as_view(), name='remove_cart_item_addition'),
    path('reject/', RejectOrderAPIView.as_view(), name='reject_order'),
    path('payment/confirm/', ConfirmLiqPayPaymentAPIView.as_view(), name='confirm_payment'),
]
