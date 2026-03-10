from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Divisao, Item, Desejo
from .serializers import DivisaoSerializer, ItemSerializer
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
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

    def total_valor(self, request):
        if request.method == "GET":
            total = Item.objects.aggregate(Sum("valor"))
            return Response({"total_valor_casa": total["valor__sum"]})


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

    divisao_id = request.GET.get("divisao")

    itens = Item.objects.all()
    desejos = Desejo.objects.all()


    if divisao_id:
        itens = itens.filter(divisao_id=divisao_id)
        desejos = desejos.filter(divisao_id=divisao_id)

    divisoes = Divisao.objects.all()

    total_itens = Item.objects.aggregate(total=Sum("valor"))["total"] or 0
    total_desejos = Desejo.objects.aggregate(total=Sum("valor"))["total"] or 0

    total_itens_count = Item.objects.count()
    total_desejos_count = Desejo.objects.count()

    context = {
        "itens": itens,
        "desejos": desejos,
        "divisoes": divisoes,
        "item_form": item_form,
        "divisao_form": divisao_form,
        "desejo_form": desejo_form,
        "total_itens": total_itens,
        "total_desejos": total_desejos,
        "total_itens_count": total_itens_count,
        "total_desejos_count": total_desejos_count,
    }

    return render(request, "inventory/dashboard.html", context)

def editar_item(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = ItemForm(instance=item)

    return render(request, "inventory/editar_item.html", {"form": form})

def editar_desejo(request, desejo_id):

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":

        form = DesejoForm(request.POST, instance=desejo)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    return redirect("dashboard")

def apagar_item(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        item.delete()

    return redirect("dashboard")

def editar_desejo(request, desejo_id):

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        form = DesejoForm(request.POST, request.FILES, instance=desejo)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = DesejoForm(instance=desejo)

    return render(request, "inventory/editar_desejo.html", {"form": form})


def apagar_desejo(request, desejo_id):

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        desejo.delete()

    return redirect("dashboard")