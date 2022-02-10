from django.urls import path

from menu.api.views import MenuItemPossibleAdditionsListAPIView

urlpatterns = [
    path('menu-items/<int:menu_item_id>/additions/', MenuItemPossibleAdditionsListAPIView.as_view(), name='menu_item_additions_list'),
]
