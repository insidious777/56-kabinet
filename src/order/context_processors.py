from order.constants import DeliveryMethods, PaymentMethods, OrderTransactionTypes


def constants(request):
    return {
        'DeliveryMethods': DeliveryMethods,
        'PaymentMethods': PaymentMethods,
        'OrderTransactionTypes': OrderTransactionTypes,
    }
