import django_filters

from menu.models import MenuCategory


class MenuCategoryFilter(django_filters.FilterSet):
    category_id = django_filters.NumberFilter(field_name='id')

    class Meta:
        model = MenuCategory
        fields = ('id',)
