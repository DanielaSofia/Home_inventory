from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Divisao, Item, Desejo, Compra, Consumivel
from .serializers import DivisaoSerializer, ItemSerializer
from django.db.models import Sum, F, Avg
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm, DivisaoForm, DesejoForm
from django.db.models.functions import TruncMonth
from django.contrib import messages

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

## Item

def itens(request):

    item_form = ItemForm()
    divisao_form = DivisaoForm()
    desejo_form = DesejoForm()

    if request.method == "POST":

        if "add_item" in request.POST:
            item_form = ItemForm(request.POST, request.FILES)
            if item_form.is_valid():
                item_form.save()
                return redirect("/")

    divisao_id = request.GET.get("divisao")

    itens = Item.objects.all()
    desejos = Desejo.objects.all()


    if divisao_id:
        itens = itens.filter(divisao_id=divisao_id)
        desejos = desejos.filter(divisao_id=divisao_id)

    divisoes = Divisao.objects.all()

    total_itens = Item.objects.aggregate(total=Sum("valor"))["total"] or 0

    total_itens_count = Item.objects.count()

    context = {
        "itens": itens,
        "divisoes": divisoes,
        "item_form": item_form,
        "divisao_form": divisao_form,
        "total_itens": total_itens,
        "total_itens_count": total_itens_count,
    }



    return render(request,"inventory/itens.html",context)

def editar_item(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()
            return redirect("itens")

    else:
        form = ItemForm(instance=item)

    return render(request, "inventory/editar_item.html", {"form": form})

def apagar_item(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        item.delete()

    return redirect("itens")

## Desejo

def desejos(request):

    desejo_form = DesejoForm()

    if request.method == "POST":

        if "add_desejo" in request.POST:
            desejo_form = DesejoForm(request.POST, request.FILES)
            if desejo_form.is_valid():
                desejo_form.save()
                return redirect("/")

    divisao_id = request.GET.get("divisao")

    desejos = Desejo.objects.all()

    if divisao_id:
        desejos = desejos.filter(divisao_id=divisao_id)

    divisoes = Divisao.objects.all()

    total_desejos = Desejo.objects.aggregate(total=Sum("valor"))["total"] or 0

    total_desejos_count = Desejo.objects.count()


    context = {
        "desejos": desejos,
        "divisoes": divisoes,
        "desejo_form": desejo_form,
        "total_desejos": total_desejos,
        "total_desejos_count": total_desejos_count,

    }



    return render(request,"inventory/desejos.html",context)

def editar_desejo(request, desejo_id):

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        form = DesejoForm(request.POST, request.FILES, instance=desejo)

        if form.is_valid():
            form.save()
            return redirect("desejo")

    else:
        form = DesejoForm(instance=desejo)

    return render(request, "inventory/editar_desejo.html", {"form": form})

def apagar_desejo(request, desejo_id):

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        desejo.delete()

    return redirect("desejo")

def comprar_desejo(request, desejo_id):
    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":

        # ✅ cria item
        Item.objects.create(
            nome=desejo.nome,
            descricao=desejo.descricao,
            valor=desejo.valor,
            quantidade=desejo.quantidade,
            divisao=desejo.divisao,
            imagem=desejo.imagem
        )

        # ❌ remove desejo
        desejo.delete()

        messages.success(request, "Item comprado e adicionado ao inventário!")

        return redirect('desejos')  # ou 'itens'

    return redirect('desejos')


def menu(request):
    return render(request, "inventory/menu.html")


def gastos(request):
    itens = Item.objects.all()

    # 💰 Total
    total = itens.aggregate(
        total=Sum(F('valor') * F('quantidade'))
    )['total'] or 0

    # 📊 Média
    media = itens.aggregate(
        media=Avg('valor')
    )['media'] or 0

    # 🏷️ Gastos por divisão
    gastos_por_divisao = itens.values('divisao__nome').annotate(
        total=Sum(F('valor') * F('quantidade'))
    ).order_by('-total')

    # 📅 Gastos por mês
    gastos_mensais = itens.annotate(
        mes=TruncMonth('data_aquisicao')
    ).values('mes').annotate(
        total=Sum(F('valor') * F('quantidade'))
    ).order_by('mes')

    return render(request, "inventory/gastos.html", {
        "itens": itens,
        "total": total,
        "media": media,
        "gastos_por_divisao": gastos_por_divisao,
        "gastos_mensais": gastos_mensais,
    })

def criar_item(request):

    if request.method == "POST":

        Item.objects.create(
            nome=request.POST.get("nome"),
            descricao=request.POST.get("descricao"),
            quantidade=request.POST.get("quantidade")
        )

    return redirect("itens")

def despensa(request):
    itens = Consumivel.objects.all().order_by('quantidade')
    divisoes = Divisao.objects.all()

    return render(request, "inventory/despensa.html", {
        "itens": itens,
        "divisoes": divisoes
    })

def lista_compras(request):
    ativos = Compra.objects.filter(comprado=False).order_by('consumivel__quantidade')
    comprados = Compra.objects.filter(comprado=True).order_by('-id')

    return render(request, "inventory/lista_compras.html", {
        "ativos": ativos,
        "comprados": comprados
    })

def adicionar_compra(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        quantidade = int(request.POST.get("quantidade") or 1)
        divisao_id = request.POST.get("divisao")

        existente = Compra.objects.filter(nome=nome, comprado=False).first()

        if existente:
            existente.quantidade += quantidade
            existente.save()
        else:
            Compra.objects.create(
                nome=nome,
                quantidade=quantidade,
                divisao_id=divisao_id  # 🔥 importante
            )

    return redirect('lista_compras')

from django.shortcuts import get_object_or_404, redirect
from .models import Consumivel

def adicionar_a_lista(item):
    existente = Compra.objects.filter(
        consumivel=item,
        comprado=False
    ).first()

    if existente:
        existente.quantidade += 1
        existente.save()
    else:
        Compra.objects.create(
            nome=item.nome,
            quantidade=1,
            divisao=item.divisao,
            consumivel=item
        )

def consumir_consumivel(request, id):
    item = get_object_or_404(Consumivel, id=id)

    if item.quantidade > 0:
        item.quantidade -= 1
        item.save()

    # 🔥 trigger automático
    if item.quantidade <= item.quantidade_minima:
        adicionar_a_lista(item)

    return redirect('despensa')

def marcar_comprado(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)

    # ✔ se tiver ligação ao consumível
    if compra.consumivel:
        compra.consumivel.quantidade += compra.quantidade
        compra.consumivel.save()

    else:
        # ⚠️ fallback (caso não esteja ligado)
        consumivel = Consumivel.objects.filter(nome=compra.nome).first()

        if consumivel:
            consumivel.quantidade += compra.quantidade
            consumivel.save()
        else:
            # 🔥 só cria se não existir mesmo
            Consumivel.objects.create(
                nome=compra.nome,
                quantidade=compra.quantidade,
                divisao=compra.divisao
            )

    compra.comprado = True
    compra.save()

    return redirect('lista_compras')


def adicionar_consumivel(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        quantidade = int(request.POST.get("quantidade") or 1)
        divisao_id = request.POST.get("divisao")

        Consumivel.objects.create(
            nome=nome,
            quantidade=quantidade,
            divisao_id=divisao_id
        )

    return redirect('despensa')

def repor_consumivel(request, id):
    item = get_object_or_404(Consumivel, id=id)

    item.quantidade += 1
    item.save()

    # 🔥 remover da lista se já não está no mínimo
    if item.quantidade > item.quantidade_minima:
        Compra.objects.filter(
            consumivel=item,
            comprado=False
        ).delete()

    return redirect('despensa')

def apagar_consumivel(request, id):
    item = get_object_or_404(Consumivel, id=id)

    if request.method == "POST":
        item.delete()

    return redirect('despensa')

def apagar_compra(request, id):
    compra = get_object_or_404(Compra, id=id)

    if request.method == "POST":
        compra.delete()

    return redirect('lista_compras')