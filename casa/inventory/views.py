"""Views web do app inventory baseadas em templates Django."""

from django.db.models import Avg, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ConsumivelForm, DesejoForm, DivisaoForm, ItemForm
from .models import Consumivel, Desejo, Divisao, Item

## Item


def itens(request):
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
    search_query = request.GET.get("q", "").strip()

    itens = Item.objects.all()
    divisoes = Divisao.objects.all()
    total_itens = Item.objects.aggregate(total=Sum("valor"))["total"] or 0
    total_itens_count = Item.objects.count()

    if divisao_id:
        itens = itens.filter(divisao_id=divisao_id)
    if search_query:
        search_filter = Q(nome__icontains=search_query) | Q(descricao__icontains=search_query)
        itens = itens.filter(search_filter)

    context = {
        "itens": itens,
        "divisoes": divisoes,
        "item_form": item_form,
        "divisao_form": divisao_form,
        "total_itens": total_itens,
        "total_itens_count": total_itens_count,
        "search_query": search_query,
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
    search_query = request.GET.get("q", "").strip()

    desejos_qs = Desejo.objects.all()

    if divisao_id:
        desejos_qs = desejos_qs.filter(divisao_id=divisao_id)
    if search_query:
        desejos_qs = desejos_qs.filter(
            Q(nome__icontains=search_query) | Q(descricao__icontains=search_query)
        )

    # 🔹 stats (usando queryset já filtrado 👌)
    total_desejos = desejos_qs.aggregate(total=Sum("valor"))["total"] or 0
    total_desejos_count = desejos_qs.count()

    context = {
        "desejos": desejos_qs,
        "divisoes": Divisao.objects.all(),
        "desejo_form": form,
        "total_desejos": total_desejos,
        "total_desejos_count": total_desejos_count,
        "search_query": search_query,
    }

    return render(request, "inventory/desejos.html", context)


def lista_compras(request):
    """Lista todos os consumíveis registados."""

    if request.method == "POST":
        form = ConsumivelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_compras")

    divisao_id = request.GET.get("divisao")
    search_query = request.GET.get("q", "").strip()
    compras = Consumivel.objects.filter(comprado=False).select_related("divisao")

    if divisao_id:
        compras = compras.filter(divisao_id=divisao_id)
    if search_query:
        compras = compras.filter(
            Q(nome__icontains=search_query) | Q(descricao__icontains=search_query)
        )

    return render(
        request,
        "inventory/lista_compras.html",
        {
            "compras": compras,
            "despensa_sugestoes": Consumivel.objects.filter(comprado=True).select_related(
                "divisao"
            ),
            "divisoes": Divisao.objects.all(),
            "search_query": search_query,
            "total_compras": compras.count(),
            "consumivel_form": ConsumivelForm(),
        },
    )


def despensa(request):
    """Lista os consumíveis já comprados e disponíveis na despensa."""

    if request.method == "POST":
        form = ConsumivelForm(request.POST)
        if form.is_valid():
            consumivel = form.save(commit=False)
            consumivel.comprado = True
            consumivel.save()
            return redirect("despensa")

    divisao_id = request.GET.get("divisao")
    search_query = request.GET.get("q", "").strip()
    consumiveis = Consumivel.objects.filter(comprado=True).select_related("divisao")

    if divisao_id:
        consumiveis = consumiveis.filter(divisao_id=divisao_id)
    if search_query:
        consumiveis = consumiveis.filter(nome__icontains=search_query)

    return render(
        request,
        "inventory/despensa.html",
        {
            "consumiveis": consumiveis,
            "divisoes": Divisao.objects.all(),
            "search_query": search_query,
            "total_consumiveis": consumiveis.count(),
            "consumivel_form": ConsumivelForm(),
        },
    )


def marcar_consumivel_comprado(request, consumivel_id):
    """Marca a compra e atualiza o stock apenas nesse momento."""

    consumivel = get_object_or_404(Consumivel, id=consumivel_id)
    if request.method == "POST":
        comprado = request.POST.get("comprado") == "on"
        quantidade_compra = request.POST.get("quantidade_compra")
        if quantidade_compra:
            consumivel.quantidade_compra = max(int(quantidade_compra), 1)
        if comprado and not consumivel.comprado:
            consumivel.quantidade += consumivel.quantidade_compra
        consumivel.comprado = comprado
        update_fields = ["comprado", "quantidade", "quantidade_compra"]
        consumivel.save(update_fields=update_fields)
    return redirect("lista_compras")


def apagar_consumivel(request, consumivel_id):
    """Apaga um consumível pendente da lista de compras."""

    consumivel = get_object_or_404(Consumivel, id=consumivel_id)
    if request.method == "POST":
        consumivel.delete()
    return redirect("lista_compras")


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
