from menu.models import MenuItem, Addition, MenuCategory


def get_menu_item_by_id(menu_item_id):
    return MenuItem.objects.filter(id=menu_item_id).first()


def get_menu_item_additions_to_show(menu_item):
    return menu_item.possible_additions.filter(show=True)


def get_menu_item_additions_by_ids(menu_item, addition_ids):
    return menu_item.possible_additions.filter(id__in=addition_ids)


def get_additions_to_show():
    return Addition.objects.filter(show=True)


def get_menu_categories_to_show():
    return MenuCategory.objects.filter(show=True).order_by('order_index')
