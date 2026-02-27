
from rest_framework import viewsets, filters
from .models import Divisao, Item
from .serializers import DivisaoSerializer, ItemSerializer

class DivisaoViewSet(viewsets.ModelViewSet):
    queryset = Divisao.objects.all()
    serializer_class = DivisaoSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'descricao']
