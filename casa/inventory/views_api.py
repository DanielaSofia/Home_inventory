"""ViewSets da API REST para o app inventory com autenticação e permissões.

Este módulo contém os ViewSets para acesso aos modelos via REST API
com autenticação, permissões e filtros configurados.
"""

import logging

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, F

from .models import Compra, Consumivel, Desejo, Divisao, HistoricoCompra, Item
from .serializers import (
    CompraSerializer, ConsumvelSerializer, DesejoSerializer,
    DivisaoSerializer, HistoricoCompraSerializer, ItemSerializer
)

logger = logging.getLogger(__name__)


class DivisaoViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir divisões da casa.
    
    Endpoints:
    - GET /api/divisoes/ - Listar todas as divisões
    - POST /api/divisoes/ - Criar nova divisão
    - GET /api/divisoes/{id}/ - Obter detalhes de uma divisão
    - PUT /api/divisoes/{id}/ - Atualizar divisão
    - DELETE /api/divisoes/{id}/ - Apagar divisão
    """

    queryset = Divisao.objects.all()
    serializer_class = DivisaoSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['nome']
    filter_backends = [filters.SearchFilter]


class ItemViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir itens da casa.
    
    Endpoints:
    - GET /api/itens/ - Listar todos os itens (com filtros)
    - POST /api/itens/ - Criar novo item
    - GET /api/itens/{id}/ - Obter detalhes de um item
    - PUT /api/itens/{id}/ - Atualizar item
    - DELETE /api/itens/{id}/ - Apagar item
    - GET /api/itens/total_valor/ - Obter valor total dos itens
    
    Query Parameters:
    - search: buscar por nome ou descrição
    - divisao: filtrar por divisão
    """

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nome", "descricao"]
    filterset_fields = ["divisao"]

    def get_serializer_context(self):
        """Inclui o `request` no contexto do serializer."""
        return {"request": self.request}

    @action(detail=False, methods=['get'])
    def total_valor(self, request):
        """Endpoint custom que retorna o total do valor dos itens."""
        try:
            total = Item.objects.aggregate(Sum("valor"))
            return Response({"total_valor_casa": total["valor__sum"]})
        except Exception as e:
            logger.error(f"Erro ao calcular total de valor: {str(e)}")
            return Response(
                {"error": "Erro ao calcular total"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatísticas dos itens."""
        try:
            stats = Item.objects.aggregate(
                total_valor=Sum("valor"),
                valor_medio=Avg("valor"),
                quantidade_total=Sum("quantidade")
            )
            return Response(stats)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return Response(
                {"error": "Erro ao obter estatísticas"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DesejoViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir lista de desejos."""

    queryset = Desejo.objects.all()
    serializer_class = DesejoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nome", "descricao"]
    filterset_fields = ["divisao"]


class CompraViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir lista de compras."""

    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["comprado", "divisao"]

    @action(detail=True, methods=['post'])
    def marcar_comprado(self, request, pk=None):
        """Marca uma compra como comprada."""
        try:
            compra = self.get_object()
            quantidade = request.data.get('quantidade', compra.quantidade)
            
            if compra.consumivel:
                compra.consumivel.quantidade += int(quantidade)
                compra.consumivel.save()
            
            compra.comprado = True
            compra.save()
            
            logger.info(f"Compra {compra.id} marcada como comprada")
            return Response({"status": "Compra marcada como comprada"})
        except Exception as e:
            logger.error(f"Erro ao marcar compra como comprada: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConsumvelViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir consumíveis (despensa)."""

    queryset = Consumivel.objects.all()
    serializer_class = ConsumvelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nome", "loja"]
    filterset_fields = ["divisao"]

    @action(detail=True, methods=['post'])
    def consumir(self, request, pk=None):
        """Decrementa a quantidade de um consumível."""
        try:
            consumivel = self.get_object()
            if consumivel.quantidade > 0:
                consumivel.quantidade -= 1
                consumivel.save()
                logger.info(f"Consumível {consumivel.id} consumido")
            return Response({"quantidade": consumivel.quantidade})
        except Exception as e:
            logger.error(f"Erro ao consumir: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def repor(self, request, pk=None):
        """Incrementa a quantidade de um consumível."""
        try:
            consumivel = self.get_object()
            quantidade = request.data.get('quantidade', 1)
            consumivel.quantidade += int(quantidade)
            consumivel.save()
            logger.info(f"Consumível {consumivel.id} reposto")
            return Response({"quantidade": consumivel.quantidade})
        except Exception as e:
            logger.error(f"Erro ao repor: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def abaixo_minimo(self, request):
        """Retorna consumíveis com quantidade abaixo do mínimo."""
        try:
            consumiveis = Consumivel.objects.filter(quantidade__lte=F('quantidade_minima'))
            serializer = self.get_serializer(consumiveis, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao listar consumíveis abaixo do mínimo: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class HistoricoCompraViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet para visualizar histórico de compras (somente leitura)."""

    queryset = HistoricoCompra.objects.all()
    serializer_class = HistoricoCompraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["consumivel", "loja"]
