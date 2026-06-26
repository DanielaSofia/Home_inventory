"""Serializers para a API do app inventory.

Contém serializers para todos os modelos incluindo campos e helpers.
"""

from rest_framework import serializers

from .models import Compra, Consumivel, Desejo, Divisao, HistoricoCompra, Item


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


class CompraSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Compra` (lista de compras)."""

    divisao_nome = serializers.CharField(source='divisao.nome', read_only=True, required=False)
    consumivel_nome = serializers.CharField(source='consumivel.nome', read_only=True, required=False)

    class Meta:
        model = Compra
        fields = [
            'id', 'nome', 'quantidade', 'comprado', 'divisao', 'divisao_nome',
            'consumivel', 'consumivel_nome'
        ]


class ConsumvelSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `Consumivel` (despensa) com histórico."""

    divisao_nome = serializers.CharField(source='divisao.nome', read_only=True)
    historico = serializers.SerializerMethodField()
    abaixo_minimo = serializers.SerializerMethodField()

    class Meta:
        model = Consumivel
        fields = [
            'id', 'nome', 'quantidade', 'quantidade_minima', 'divisao',
            'divisao_nome', 'preco', 'loja', 'historico', 'abaixo_minimo'
        ]

    def get_historico(self, obj):
        """Retorna o histórico de compras do consumível."""
        historico = obj.historico.all().order_by('-data')[:5]
        return HistoricoCompraSerializer(historico, many=True, read_only=True).data

    def get_abaixo_minimo(self, obj):
        """Indica se a quantidade está abaixo do mínimo."""
        return obj.quantidade <= obj.quantidade_minima


class HistoricoCompraSerializer(serializers.ModelSerializer):
    """Serializer para o modelo `HistoricoCompra`."""

    consumivel_nome = serializers.CharField(source='consumivel.nome', read_only=True)

    class Meta:
        model = HistoricoCompra
        fields = ['id', 'consumivel', 'consumivel_nome', 'quantidade', 'preco', 'loja', 'data']
        read_only_fields = ['data']
