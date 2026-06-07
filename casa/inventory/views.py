"""Views do app inventory: views baseadas em Django e ViewSets da API.

Este módulo contém as views usadas pela aplicação web (renderização
de templates) e os ViewSets da API REST.
"""

from django.core.paginator import Paginator
from django.db.models import Avg, F, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.response import Response

from .forms import DesejoForm, DivisaoForm, ItemForm
from .models import Compra, Consumivel, Desejo, Divisao, Item
from .serializers import DivisaoSerializer, ItemSerializer


class DivisaoViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir divisões da casa."""

    queryset = Divisao.objects.all()
    serializer_class = DivisaoSerializer


class ItemViewSet(viewsets.ModelViewSet):
    """API ViewSet para gerir itens da casa."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nome", "descricao"]
    filterset_fields = ["divisao"]

    def get_serializer_context(self):
        """Inclui o `request` no contexto do serializer."""

        return {"request": self.request}

    def total_valor(self, request):
        """Endpoint custom que retorna o total do valor dos itens."""

        if request.method == "GET":
            total = Item.objects.aggregate(Sum("valor"))
            return Response({"total_valor_casa": total["valor__sum"]})


## Item


def listar_itens(request):
    """Renderiza a listagem de itens e trata a criação via formulário.

    Mostra também filtros por divisão e estatísticas básicas.
    """

    item_form = ItemForm()
    divisao_form = DivisaoForm()

    if request.method == "POST":

        if "add_item" in request.POST:
            item_form = ItemForm(request.POST, request.FILES)
            if item_form.is_valid():
                item_form.save()
                return redirect("/")

    divisao_id = request.GET.get("divisao")

    itens = Item.objects.all()
    divisoes = Divisao.objects.all()
    total_itens = Item.objects.aggregate(total=Sum("valor"))["total"] or 0
    total_itens_count = Item.objects.count()

    if divisao_id:
        itens = itens.filter(divisao_id=divisao_id)

    # paginação
    paginator = Paginator(itens.order_by("nome"), 24)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    # fornecer `itens` como page_obj para compatibilidade com template
    itens = page_obj

    context = {
        "itens": itens,
        "page_obj": page_obj,
        "divisoes": divisoes,
        "item_form": item_form,
        "divisao_form": divisao_form,
        "total_itens": total_itens,
        "total_itens_count": total_itens_count,
    }

    return render(request, "inventory/itens.html", context)


def criar_item(request):
    """Cria um `Item` simples a partir de `POST` e redireciona para `itens`.

    Usa apenas campos mínimos (`nome`, `descricao`, `quantidade`).
    """

    if request.method == "POST":

        Item.objects.create(
            nome=request.POST.get("nome"),
            descricao=request.POST.get("descricao"),
            quantidade=request.POST.get("quantidade"),
        )

    return redirect("itens")


def editar_item(request, item_id):
    """Renderiza e processa o formulário de edição para um `Item`.

    `item_id` identifica o item a editar.
    """

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
    """Apaga um `Item` após confirmação via `POST` e redireciona para `itens`."""

    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        item.delete()

    return redirect("itens")


## Desejo


def desejos(request):
    """Lista desejos, processa criação e mostra estatísticas simples."""

    # 🔹 formulário
    if request.method == "POST" and "add_desejo" in request.POST:
        form = DesejoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("desejos")
    else:
        form = DesejoForm()

    # 🔹 filtro
    divisao_id = request.GET.get("divisao")

    desejos_qs = Desejo.objects.all()

    if divisao_id:
        desejos_qs = desejos_qs.filter(divisao_id=divisao_id)

    # 🔹 stats (usando queryset já filtrado 👌)
    total_desejos = desejos_qs.aggregate(total=Sum("valor"))["total"] or 0
    total_desejos_count = desejos_qs.count()

    context = {
        "desejos": desejos_qs,
        "divisoes": Divisao.objects.all(),
        "desejo_form": form,
        "total_desejos": total_desejos,
        "total_desejos_count": total_desejos_count,
    }

    return render(request, "inventory/desejos.html", context)


def editar_desejo(request, desejo_id):
    """Edita um `Desejo` identificado por `desejo_id`."""

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        form = DesejoForm(request.POST, request.FILES, instance=desejo)

        if form.is_valid():
            form.save()
            return redirect("desejos")

    else:
        form = DesejoForm(instance=desejo)

    return render(request, "inventory/editar_desejo.html", {"form": form})


def apagar_desejo(request, desejo_id):
    """Apaga um `Desejo` após confirmação via `POST`."""

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        desejo.delete()

    return redirect("desejos")


def comprar_desejo(request, desejo_id):
    """Converte um `Desejo` em `Item` (compra) e remove o desejo.

    Recebe dados opcionais como `data` e `preco` via `POST`.
    """

    desejo = get_object_or_404(Desejo, id=desejo_id)

    if request.method == "POST":
        data = request.POST.get("data")
        preco = request.POST.get("preco")

        Item.objects.create(
            nome=desejo.nome,
            descricao=desejo.descricao,
            data_aquisicao=data,
            valor=preco if preco else None,
            divisao=desejo.divisao,  # 🔥 importante
        )

        desejo.delete()

    return redirect("itens")


## MENU


def menu(request):
    """Renderiza o menu principal do app inventory."""

    return render(request, "inventory/menu.html")


def dashboard(request):
    """Página de dashboard com métricas rápidas do inventário."""

    itens = Item.objects.all()

    # total de unidades (soma das quantidades dos itens)
    total_unidades = itens.aggregate(total=Sum("quantidade"))["total"] or 0

    # valor total considerando quantidade * valor por item
    total_valor = itens.aggregate(total=Sum(F("valor") * F("quantidade")))["total"] or 0

    # divisões com maior valor
    top_divisoes = (
        itens.values("divisao__nome")
        .annotate(total=Sum(F("valor") * F("quantidade")))
        .order_by("-total")
    )

    # consumíveis em alerta (abaixo ou igual ao mínimo)
    consumiveis_alerta = Consumivel.objects.filter(quantidade__lte=F("quantidade_minima"))

    # itens adicionados recentemente
    recentes = Item.objects.order_by("-data_adicionado")[:5]

    # gastos mensais para gráfico
    gastos_mensais_qs = (
        itens.annotate(mes=TruncMonth("data_aquisicao"))
        .values("mes")
        .annotate(total=Sum(F("valor") * F("quantidade")))
        .order_by("mes")
    )

    # preparar labels/valores para o chart (JSON)
    import json

    labels = [g["mes"].strftime("%b %Y") if g.get("mes") else "" for g in gastos_mensais_qs]
    values = [float(g.get("total") or 0) for g in gastos_mensais_qs]

    context = {
        "total_unidades": total_unidades,
        "total_valor": total_valor,
        "top_divisoes": top_divisoes,
        "consumiveis_alerta": consumiveis_alerta,
        "recentes": recentes,
        "gastos_mensais_labels": json.dumps(labels),
        "gastos_mensais_values": json.dumps(values),
    }

    return render(request, "inventory/dashboard.html", context)


## Gastos


def gastos(request):
    """Gera a página de gastos com agregações e relatórios simples."""
    itens = Item.objects.all()

    # 💰 Total
    total = itens.aggregate(total=Sum(F("valor") * F("quantidade")))["total"] or 0

    # 📊 Média
    media = itens.aggregate(media=Avg("valor"))["media"] or 0

    # 🏷️ Gastos por divisão
    gastos_por_divisao = (
        itens.values("divisao__nome")
        .annotate(total=Sum(F("valor") * F("quantidade")))
        .order_by("-total")
    )

    # 📅 Gastos por mês
    gastos_mensais = (
        itens.annotate(mes=TruncMonth("data_aquisicao"))
        .values("mes")
        .annotate(total=Sum(F("valor") * F("quantidade")))
        .order_by("mes")
    )

    return render(
        request,
        "inventory/gastos.html",
        {
            "itens": itens,
            "total": total,
            "media": media,
            "gastos_por_divisao": gastos_por_divisao,
            "gastos_mensais": gastos_mensais,
        },
    )


## Despensa


def despensa(request):
    """Mostra a lista de consumíveis (despensa) com filtros e pesquisa."""
    divisao_id = request.GET.get("divisao")
    query = request.GET.get("q")

    itens = Consumivel.objects.select_related("divisao").all()

    if divisao_id:
        itens = itens.filter(divisao_id=divisao_id)

    if query:
        itens = itens.filter(nome__icontains=query)

    itens = itens.order_by("nome")

    divisoes = Divisao.objects.all()

    return render(
        request,
        "inventory/despensa.html",
        {"itens": itens, "divisoes": divisoes, "divisao_selecionada": divisao_id, "query": query},
    )


def consumir_consumivel(_request, consumivel_id):
    """Decrementa a quantidade de um `Consumivel` e adiciona à lista se necessário."""

    item = get_object_or_404(Consumivel, id=consumivel_id)

    # 🔒 evitar negativos + update atómico
    if item.quantidade > 0:
        Consumivel.objects.filter(id=item.id).update(quantidade=F("quantidade") - 1)

        # atualizar valor em memória
        item.quantidade -= 1

    # 🔥 trigger automático
    if item.quantidade <= item.quantidade_minima:
        adicionar_a_lista(item)

    return redirect("despensa")


def adicionar_consumivel(request):
    """Adiciona um novo `Consumivel` via `POST` e redireciona para `despensa`."""

    if request.method == "POST":
        nome = request.POST.get("nome")
        quantidade = int(request.POST.get("quantidade") or 1)
        divisao_id = request.POST.get("divisao")
        preco = request.POST.get("preco")
        loja = request.POST.get("loja")

        Consumivel.objects.create(
            nome=nome,
            quantidade=quantidade,
            divisao_id=divisao_id,
            preco=preco if preco else None,
            loja=loja,
        )

    return redirect("despensa")


def repor_consumivel(_request, consumivel_id):
    """Repondo a quantidade de um `Consumivel` e limpa a lista de compras se necessário."""

    item = get_object_or_404(Consumivel, id=consumivel_id)

    item.quantidade += 1
    item.save()

    # 🔥 remover da lista se já não está no mínimo
    if item.quantidade > item.quantidade_minima:
        Compra.objects.filter(consumivel=item, comprado=False).delete()

    return redirect("despensa")


def apagar_consumivel(request, consumivel_id):
    """Apaga um `Consumivel` após confirmação via `POST`."""

    item = get_object_or_404(Consumivel, id=consumivel_id)

    if request.method == "POST":
        item.delete()

    return redirect("despensa")


## Lista Compras
def lista_compras(request):
    """Mostra a lista de compras dividida entre ativos e comprados."""

    ativos = Compra.objects.filter(comprado=False)
    comprados = Compra.objects.filter(comprado=True)

    divisoes = Divisao.objects.all()

    return render(
        request,
        "inventory/lista_compras.html",
        {"ativos": ativos, "comprados": comprados, "divisoes": divisoes},
    )


def adicionar_compra(request):
    """Adiciona uma `Compra` (ou incrementa se já existir) a partir de `POST`."""

    if request.method == "POST":
        nome = request.POST.get("nome")
        quantidade = int(request.POST.get("quantidade") or 1)
        divisao_id = request.POST.get("divisao")

        # opcional: tentar ligar a um consumível existente
        consumivel = Consumivel.objects.filter(nome__iexact=nome).first()

        existente = Compra.objects.filter(nome__iexact=nome, comprado=False).first()

        if existente:
            existente.quantidade += quantidade
            existente.save()
        else:
            Compra.objects.create(
                nome=nome,
                quantidade=quantidade,
                divisao_id=divisao_id,
                consumivel=consumivel,  # pode ser None
            )

    return redirect("lista_compras")


def adicionar_a_lista(item):
    """Adiciona um `Consumivel` à lista de compras se ainda não existir."""

    existente = Compra.objects.filter(consumivel=item, comprado=False).first()

    if not existente:
        Compra.objects.create(nome=item.nome, quantidade=1, divisao=item.divisao, consumivel=item)


def marcar_comprado(request, compra_id):
    """Marca uma `Compra` como comprada, atualizando stock ou criando consumível."""

    compra = get_object_or_404(Compra, id=compra_id)

    if request.method == "POST":

        quantidade = int(request.POST.get("quantidade") or compra.quantidade)

        if compra.consumivel:

            # 🔥 atualizar stock corretamente
            compra.consumivel.quantidade += quantidade
            compra.consumivel.save()

        else:
            # 🔥 criar apenas se não existir
            consumivel = Consumivel.objects.filter(nome=compra.nome).first()

            if consumivel:
                consumivel.quantidade += quantidade
                consumivel.save()
            else:
                consumivel = Consumivel.objects.create(
                    nome=compra.nome, quantidade=quantidade, divisao=compra.divisao
                )

            compra.consumivel = consumivel

        compra.comprado = True
        compra.save()

    return redirect("lista_compras")


def apagar_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)

    if request.method == "POST":
        compra.delete()

    return redirect("lista_compras")
