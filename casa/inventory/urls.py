from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    DivisaoViewSet,
    ItemViewSet,
    editar_desejo,
    editar_item,
    apagar_item,
    apagar_desejo,
    menu,
    itens,
    desejos,
    compras,
    gastos,
    comprar_item,
    apagar_compra,
    criar_item, comprar_desejo, despensa
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
    path("compras/", compras, name="compras"),
    path("compras/<int:id>/", comprar_item, name="comprar_item"),
    path("apagar-compra/<int:id>/", apagar_compra, name="apagar_compra"),
    path("criar-item/", criar_item, name="criar_item"),
    path("despensa/", despensa, name="despensa"),

    path("editar-item/<int:item_id>/", editar_item, name="editar_item"),
    path("apagar-item/<int:item_id>/", apagar_item, name="apagar_item"),
    path("editar-desejo/<int:desejo_id>/", editar_desejo, name="editar_desejo"),
    path("apagar-desejo/<int:desejo_id>/", apagar_desejo, name="apagar_desejo"),
]
