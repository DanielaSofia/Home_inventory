"""Views web do app inventory baseadas em templates Django.

Este módulo contém as views usadas pela aplicação web (renderização
de templates) e os ViewSets da API REST.
"""

from decimal import InvalidOperation

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ConsumivelForm, DesejoForm, DivisaoForm, ItemForm, parse_fractional_decimal
from .models import Consumivel, Desejo, Divisao, Item


def service_worker(request):
    """Serve o service worker a partir da raiz para que o seu scope cubra todo o site."""

    sw_path = (
        settings.BASE_DIR
        / "casa"
        / "inventory"
        / "static"
        / "inventory"
        / "js"
        / "service-worker.js"
    )
    return HttpResponse(sw_path.read_text(), content_type="application/javascript")


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
        "divisao_selecionada": divisao_id,
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
            "ativos": compras,
            "lista": compras,
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
            "itens": consumiveis,
            "divisoes": Divisao.objects.all(),
            "search_query": search_query,
            "query": search_query,
            "divisao_selecionada": divisao_id,
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
            try:
                quantidade_compra = parse_fractional_decimal(quantidade_compra)
            except (InvalidOperation, ValueError, TypeError):
                quantidade_compra = None
            if quantidade_compra and quantidade_compra > 0:
                consumivel.quantidade_compra = quantidade_compra
        if comprado and not consumivel.comprado:
            consumivel.quantidade += consumivel.quantidade_compra
        consumivel.comprado = comprado
        update_fields = ["comprado", "quantidade", "quantidade_compra", "updated_at"]
        consumivel.save(update_fields=update_fields)
    return redirect("lista_compras")


def adicionar_compra(request):
    """Adiciona um consumível pendente à lista de compras."""

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        divisao_id = request.POST.get("divisao")
        quantidade = request.POST.get("quantidade", "1")
        if nome and divisao_id:
            try:
                quantidade = parse_fractional_decimal(quantidade)
            except (InvalidOperation, ValueError, TypeError):
                quantidade = None
            if quantidade is not None and quantidade > 0:
                consumivel, criado = Consumivel.objects.get_or_create(
                    nome=nome,
                    divisao_id=divisao_id,
                    comprado=False,
                    defaults={"quantidade_compra": quantidade},
                )
                if not criado:
                    consumivel.quantidade_compra += quantidade
                    consumivel.save(update_fields=["quantidade_compra", "updated_at"])
    return redirect("lista_compras")


def marcar_comprado(request, compra_id):
    """Marca um consumível como comprado e atualiza o stock."""

    consumivel = get_object_or_404(Consumivel, id=compra_id)
    if request.method == "POST" and not consumivel.comprado:
        quantidade = request.POST.get("quantidade", consumivel.quantidade_compra)
        try:
            quantidade = parse_fractional_decimal(quantidade)
        except (InvalidOperation, ValueError, TypeError):
            quantidade = consumivel.quantidade_compra
        if quantidade > 0:
            consumivel.quantidade += quantidade
        consumivel.comprado = True
        consumivel.save(update_fields=["quantidade", "comprado", "updated_at"])
    return redirect("lista_compras")


def apagar_compra(request, compra_id):
    """Remove um consumível pendente da lista de compras."""

    consumivel = get_object_or_404(Consumivel, id=compra_id)
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


def dashboard(request):
    """Página de dashboard com métricas rápidas do inventário."""

    itens = Item.objects.all()

    # total de unidades (soma das quantidades dos itens)
    total_unidades = itens.aggregate(total=Sum("quantidade"))["total"] or 0

    # valor total considerando quantidade * valor por item
    total_valor = itens.aggregate(total=Sum(F("valor") * F("quantidade")))["total"] or 0

    # consumíveis em alerta (abaixo ou igual ao mínimo)
    consumiveis_alerta = Consumivel.objects.filter(quantidade__lte=F("quantidade_compra"))

    # itens adicionados recentemente
    recentes = Item.objects.order_by("-data_adicionado")[:5]

    context = {
        "total_unidades": total_unidades,
        "total_valor": total_valor,
        "consumiveis_alerta": consumiveis_alerta,
        "recentes": recentes,
    }

    return render(request, "inventory/dashboard.html", context)


def consumir_consumivel(_request, consumivel_id):
    """Decrementa a quantidade de um consumível comprado."""

    item = get_object_or_404(Consumivel, id=consumivel_id)

    if item.quantidade > 0:
        Consumivel.objects.filter(id=consumivel_id).update(quantidade=F("quantidade") - 1)
        item.quantidade -= 1
    if item.quantidade <= 0:
        item.comprado = False
        item.save(update_fields=["quantidade", "comprado", "updated_at"])

    return redirect("despensa")


def adicionar_consumivel(request):
    """Adiciona um novo consumível via formulário e redireciona para a despensa."""

    if request.method == "POST":
        form = ConsumivelForm(request.POST)
        if form.is_valid():
            consumivel = form.save(commit=False)
            consumivel.comprado = True
            consumivel.save()

    return redirect("despensa")


def repor_consumivel(_request, consumivel_id):
    """Repõe uma unidade de um consumível e marca-o como disponível."""

    item = get_object_or_404(Consumivel, id=consumivel_id)

    item.quantidade += 1
    item.comprado = True
    item.save(update_fields=["quantidade", "comprado", "updated_at"])

    return redirect("despensa")


def apagar_consumivel(request, consumivel_id):
    """Apaga um `Consumivel` após confirmação via `POST`."""

    item = get_object_or_404(Consumivel, id=consumivel_id)

    if request.method == "POST":
        item.delete()

    return redirect("despensa")
