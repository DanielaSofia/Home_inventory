"""Serializers para a API do app inventory.

Contém serializers para `Item` e `Divisao` incluindo campos e helpers.
"""

from rest_framework import serializers

from .models import Divisao, Item


class ItemSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Item`."""

    class Meta:
        model = Item
        fields = "__all__"

    def get_imagem_url(self, obj):
        """Retorna a URL absoluta da imagem do item, quando disponível.

        Usa o `request` presente no contexto do serializer para construir a URL.
        """

        request = self.context.get("request")
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None


class DivisaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Divisao` incluindo os itens relacionados."""

    itens = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Divisao
        fields = "__all__"
