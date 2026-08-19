"""URLs do app inventory.

Regista rotas da API e views baseadas em função usadas pela interface.
"""

from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import (
    apagar_consumivel,
    apagar_desejo,
    apagar_item,
    comprar_desejo,
    criar_item,
    desejos,
    despensa,
    editar_desejo,
    editar_item,
    gastos,
    itens,
    lista_compras,
    marcar_consumivel_comprado,
    menu,
)
from .views_api import DesejoViewSet, DivisaoViewSet, ItemViewSet

# API Router
router = DefaultRouter()
router.register(r"divisoes", DivisaoViewSet, basename="divisao")
router.register(r"itens", ItemViewSet, basename="item")
router.register(r"desejos", DesejoViewSet, basename="desejo")

urlpatterns = [
    # API Routes
    path("api/", include(router.urls)),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    # Web Views (Traditional Django Templates)
    path("", menu, name="menu"),
    path("itens/", itens, name="itens"),
    path("desejos/", desejos, name="desejos"),
    path("lista-compras/", lista_compras, name="lista_compras"),
    path("despensa/", despensa, name="despensa"),
    path(
        "marcar-consumivel-comprado/<int:consumivel_id>/",
        marcar_consumivel_comprado,
        name="marcar_consumivel_comprado",
    ),
    path("apagar-consumivel/<int:consumivel_id>/", apagar_consumivel, name="apagar_consumivel"),
    path("comprar-desejo/<int:desejo_id>/", comprar_desejo, name="comprar_desejo"),
    path("gastos/", gastos, name="gastos"),
    path("criar-item/", criar_item, name="criar_item"),
    path("editar-item/<int:item_id>/", editar_item, name="editar_item"),
    path("apagar-item/<int:item_id>/", apagar_item, name="apagar_item"),
    path("editar-desejo/<int:desejo_id>/", editar_desejo, name="editar_desejo"),
    path("apagar-desejo/<int:desejo_id>/", apagar_desejo, name="apagar_desejo"),
]
