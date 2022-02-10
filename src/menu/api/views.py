from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView

from common.decorators import forbidden_for_authenticated
from menu.api.serializers import AdditionSerializer
from menu.repository.menu_item import get_menu_item_by_id, get_menu_item_additions_to_show


@method_decorator(forbidden_for_authenticated, name='get')
class MenuItemPossibleAdditionsListAPIView(APIView):

    def get(self, request, menu_item_id):
        menu_item = get_menu_item_by_id(menu_item_id)

        if menu_item is None:
            raise Http404()

        additions = get_menu_item_additions_to_show(menu_item)

        return Response(AdditionSerializer(additions, many=True).data)
