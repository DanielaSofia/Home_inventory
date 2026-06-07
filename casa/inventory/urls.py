"""URLs do app inventory.

Regista rotas da API e views baseadas em função usadas pela interface.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DivisaoViewSet,
    ItemViewSet,
    adicionar_compra,
    adicionar_consumivel,
    apagar_compra,
    apagar_consumivel,
    apagar_desejo,
    apagar_item,
    comprar_desejo,
    consumir_consumivel,
    criar_item,
    dashboard,
    desejos,
    despensa,
    editar_desejo,
    editar_item,
    gastos,
    lista_compras,
    listar_itens,
    marcar_comprado,
    menu,
    repor_consumivel,
)

router = DefaultRouter()
router.register(r"divisoes", DivisaoViewSet)
router.register(r"itens", ItemViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("", menu, name="menu"),
    path("dashboard/", dashboard, name="dashboard"),
    path("itens/", listar_itens, name="itens"),
    path("desejos/", desejos, name="desejos"),
    path("comprar-desejo/<int:desejo_id>/", comprar_desejo, name="comprar_desejo"),
    path("gastos/", gastos, name="gastos"),
    path("lista-compras/", lista_compras, name="lista_compras"),
    path("comprado/<int:compra_id>/", marcar_comprado, name="marcar_comprado"),
    path("criar-item/", criar_item, name="criar_item"),
    path("despensa/", despensa, name="despensa"),
    path("editar-item/<int:item_id>/", editar_item, name="editar_item"),
    path("apagar-item/<int:item_id>/", apagar_item, name="apagar_item"),
    path("editar-desejo/<int:desejo_id>/", editar_desejo, name="editar_desejo"),
    path("apagar-desejo/<int:desejo_id>/", apagar_desejo, name="apagar_desejo"),
    path("adicionar-compra/", adicionar_compra, name="adicionar_compra"),
    path("adicionar-consumivel/", adicionar_consumivel, name="adicionar_consumivel"),
    path("consumir/<int:consumivel_id>/", consumir_consumivel, name="consumir_consumivel"),
    path("repor/<int:consumivel_id>/", repor_consumivel, name="repor_consumivel"),
    path("apagar-consumivel/<int:consumivel_id>/", apagar_consumivel, name="apagar_consumivel"),
    path("apagar-compra/<int:compra_id>/", apagar_compra, name="apagar_compra"),
]
