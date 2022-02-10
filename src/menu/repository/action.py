from menu.models import Action


def get_actual_actions():
    return Action.objects.filter(show=True).order_by('order_index')
