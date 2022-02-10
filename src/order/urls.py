from django.urls import path

from order.views import CartView, PaymentView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('payment/', PaymentView.as_view(), name='payment'),
]
