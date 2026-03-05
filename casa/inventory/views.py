from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Divisao, Item
from .serializers import DivisaoSerializer, ItemSerializer
from django.db.models import Sum
from django.shortcuts import render,redirect
from .forms import ItemForm, DivisaoForm

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
    query = request.GET.get("q")
    divisao_id = request.GET.get("divisao")

    itens = Item.objects.select_related("divisao")

    itens_reais = Item.objects.filter(is_desejo=False)
    itens_desejo = Item.objects.filter(is_desejo=True)

    if query:
        itens_reais = itens_reais.filter(Q(nome__icontains=query) | Q(descricao__icontains=query))
        itens_desejo = itens_desejo.filter(Q(nome__icontains=query) | Q(descricao__icontains=query))

    if divisao_id:
        itens_reais = itens_reais.filter(divisao_id=divisao_id)
        itens_desejo = itens_desejo.filter(divisao_id=divisao_id)

    total_adquirido = itens_reais.aggregate(Sum('valor_estimado'))['valor_estimado__sum'] or 0
    total_desejos = itens_desejo.aggregate(Sum('valor_estimado'))['valor_estimado__sum'] or 0

    # 👇 FORM
    if request.method == "POST":

        if "add_item" in request.POST:
            item_form = ItemForm(request.POST, request.FILES)
            divisao_form = DivisaoForm()
            if item_form.is_valid():
                item_form.save()
                return redirect("dashboard")

        elif "add_divisao" in request.POST:
            divisao_form = DivisaoForm(request.POST)
            item_form = ItemForm()
            if divisao_form.is_valid():
                divisao_form.save()
                return redirect("dashboard")

    else:
        item_form = ItemForm()
        divisao_form = DivisaoForm()

    context = {
        "itens_reais": itens_reais,
        "itens_desejo": itens_desejo,
        "total_adquirido": total_adquirido,
        "total_desejos": total_desejos,
        "form": item_form,
        "divisao_form": divisao_form,
        }

    return render(request, "inventory/dashboard.html", context)
