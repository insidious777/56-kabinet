from order.models import Customer


def get_or_create_customer(name, phone_number):
    return Customer.objects.get_or_create(phone_number=phone_number, defaults={'name': name})
