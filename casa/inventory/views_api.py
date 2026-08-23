"""ViewSets da API REST para o app inventory com autenticação e permissões.

Este módulo contém os ViewSets para acesso aos modelos via REST API
com autenticação, permissões e filtros configurados.
"""

import logging

from django.db.models import Avg, Sum
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Consumivel, Desejo, Divisao, Item
from .serializers import ConsumivelSerializer, DesejoSerializer, DivisaoSerializer, ItemSerializer

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


class ConsumivelViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir consumíveis (lista de compras / despensa)."""

    queryset = Consumivel.objects.all()
    serializer_class = ConsumivelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nome"]
    filterset_fields = ["divisao", "comprado"]


class ConsumivelSyncView(APIView):
    """Sincronização offline-first de `Consumivel` para a PWA.

    GET  ?since=<isoformat> -> alterações no servidor desde essa data.
    POST {"consumiveis": [...], "apagados": [uuid, ...]} -> aplica alterações feitas offline.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        since = parse_datetime(request.query_params.get("since", "") or "")
        queryset = Consumivel.objects.select_related("divisao").all()
        if since:
            queryset = queryset.filter(updated_at__gt=since)
        return Response({
            "server_time": timezone.now().isoformat(),
            "consumiveis": ConsumivelSerializer(queryset, many=True).data,
        })

    def post(self, request):
        aplicados = []
        erros = []

        for item in request.data.get("consumiveis", []):
            item_uuid = item.get("uuid")
            if not item_uuid:
                erros.append({"uuid": None, "erro": "uuid em falta"})
                continue
            instance = Consumivel.objects.filter(uuid=item_uuid).first()
            serializer = ConsumivelSerializer(instance, data=item, partial=True)
            if serializer.is_valid():
                serializer.save(uuid=item_uuid)
                aplicados.append(item_uuid)
            else:
                erros.append({"uuid": item_uuid, "erro": serializer.errors})

        apagados = request.data.get("apagados", [])
        if apagados:
            Consumivel.objects.filter(uuid__in=apagados).delete()

        return Response({
            "server_time": timezone.now().isoformat(),
            "aplicados": aplicados,
            "apagados": apagados,
            "erros": erros,
        }, status=status.HTTP_207_MULTI_STATUS if erros else status.HTTP_200_OK)
