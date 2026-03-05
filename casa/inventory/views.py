from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Divisao, Item, Desejo
from .serializers import DivisaoSerializer, ItemSerializer
from django.db.models import Sum
from django.shortcuts import render, redirect
from .forms import ItemForm, DivisaoForm, DesejoForm


class DivisaoViewSet(viewsets.ModelViewSet):
    queryset = Divisao.objects.all()
    serializer_class = DivisaoSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nome", "descricao"]
    filterset_fields = ["divisao"]

    def get_serializer_context(self):
        return {"request": self.request}

    # @action(detail=False, methods=['get'])
    def total_valor(self, request):
        total = Item.objects.aggregate(Sum("valor_estimado"))
        return Response({"total_valor_casa": total["valor_estimado__sum"]})


def dashboard(request):

    item_form = ItemForm()
    divisao_form = DivisaoForm()
    desejo_form = DesejoForm()

    if request.method == "POST":

        if "add_item" in request.POST:
            item_form = ItemForm(request.POST, request.FILES)
            if item_form.is_valid():
                item_form.save()
                return redirect("/")

        elif "add_divisao" in request.POST:
            divisao_form = DivisaoForm(request.POST)
            if divisao_form.is_valid():
                divisao_form.save()
                return redirect("/")

        elif "add_desejo" in request.POST:
            desejo_form = DesejoForm(request.POST, request.FILES)
            if desejo_form.is_valid():
                desejo_form.save()
                return redirect("/")

    itens = Item.objects.all()
    desejos = Desejo.objects.all()
    divisoes = Divisao.objects.all()

    total_itens = Item.objects.aggregate(total=Sum("valor_estimado"))["total"] or 0
    total_desejos = Desejo.objects.aggregate(total=Sum("valor_estimado"))["total"] or 0

    context = {
        "itens": itens,
        "desejos": desejos,
        "divisoes": divisoes,
        "item_form": item_form,
        "divisao_form": divisao_form,
        "desejo_form": desejo_form,
        "total_itens": total_itens,
        "total_desejos": total_desejos,
    }

    return render(request, "inventory/dashboard.html", context)
