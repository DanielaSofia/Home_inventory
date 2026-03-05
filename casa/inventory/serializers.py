
from rest_framework import serializers
from .models import Divisao, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None

class DivisaoSerializer(serializers.ModelSerializer):
    itens = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Divisao
        fields = '__all__'
