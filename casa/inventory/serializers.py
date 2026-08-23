"""Serializers para a API do app inventory.

Contém serializers para os modelos ativos incluindo campos e helpers.
"""

from rest_framework import serializers

from .models import Consumivel, Desejo, Divisao, Item

class DivisaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Divisao` incluindo os itens relacionados."""

    itens = serializers.SerializerMethodField()

    class Meta:
        model = Divisao
        fields = ['id', 'nome', 'itens']

    def get_itens(self, obj):
        """Retorna itens relacionados usando ItemSerializer."""
        items = obj.itens.all()
        return ItemSerializer(items, many=True, read_only=True).data


class ItemSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Item` com informações completas."""

    divisao_nome = serializers.CharField(source='divisao.nome', read_only=True)
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'divisao', 'divisao_nome', 'nome', 'descricao',
            'quantidade', 'imagem', 'imagem_url', 'data_adicionado',
            'valor', 'data_aquisicao'
        ]
        read_only_fields = ['data_adicionado']

    def get_imagem_url(self, obj):
        """Retorna a URL absoluta da imagem do item."""
        request = self.context.get("request")
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None


class DesejoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Desejo` com informações completas."""

    divisao_nome = serializers.CharField(source='divisao.nome', read_only=True, required=False)
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = Desejo
        fields = [
            'id', 'nome', 'descricao', 'valor', 'imagem', 'imagem_url',
            'divisao', 'divisao_nome', 'quantidade'
        ]

    def get_imagem_url(self, obj):
        """Retorna a URL absoluta da imagem do desejo."""
        request = self.context.get("request")
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None


class ConsumivelSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Consumivel` usado na API e na sincronização offline."""

    divisao_nome = serializers.CharField(source='divisao.nome', read_only=True)

    class Meta:
        model = Consumivel
        fields = [
            'id', 'uuid', 'nome', 'quantidade', 'quantidade_compra',
            'comprado', 'divisao', 'divisao_nome', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']
