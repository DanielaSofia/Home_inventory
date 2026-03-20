from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    DivisaoViewSet, ItemViewSet,
    menu,
    editar_desejo,
    itens, criar_item, editar_item, apagar_item,
    desejos, apagar_desejo, comprar_desejo,
    gastos,
    despensa, marcar_comprado, lista_compras, adicionar_compra,  apagar_compra,
    adicionar_consumivel, consumir_consumivel, repor_consumivel, apagar_consumivel
)
from django.urls import include

router = DefaultRouter()
router.register(r"divisoes", DivisaoViewSet)
router.register(r"itens", ItemViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("", menu, name="menu"),
    path("itens/", itens, name="itens"),
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
    path("consumir/<int:id>/", consumir_consumivel, name="consumir_consumivel"),
    path("repor/<int:id>/", repor_consumivel, name="repor_consumivel"),
    path("apagar-consumivel/<int:id>/", apagar_consumivel, name="apagar_consumivel"),
    path("apagar-compra/<int:id>/", apagar_compra, name="apagar_compra"),
]
