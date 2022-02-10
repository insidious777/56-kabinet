from rest_framework import serializers

from menu.models import Addition


class AdditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Addition
        fields = ('id', 'title', 'price')
