"""URLs do app inventory.

Regista rotas da API e views baseadas em função usadas pela interface.
"""

from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import (
    adicionar_compra,
    adicionar_consumivel,
    apagar_compra,
    apagar_consumivel,
    apagar_desejo,
    apagar_item,
    atualizar_quantidade_consumivel,
    comprar_desejo,
    consumir_consumivel,
    criar_item,
    dashboard,
    definicoes,
    desejos,
    despensa,
    editar_desejo,
    editar_item,
    lista_compras,
    listar_itens,
    marcar_consumivel_comprado,
    menu,
    pwa_diagnostico,
    repor_consumivel,
    service_worker,
)
from .views_api import (
    ConsumivelSyncView,
    ConsumivelViewSet,
    DesejoViewSet,
    DivisaoViewSet,
    ItemViewSet,
)

# API Router
router = DefaultRouter()
router.register(r"divisoes", DivisaoViewSet, basename="divisao")
router.register(r"itens", ItemViewSet, basename="item")
router.register(r"desejos", DesejoViewSet, basename="desejo")
router.register(r"consumiveis", ConsumivelViewSet, basename="consumivel")

urlpatterns = [
    # API Routes
    path("api/", include(router.urls)),
    path("api/sync/consumiveis/", ConsumivelSyncView.as_view(), name="sync_consumiveis"),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    # PWA
    path("service-worker.js", service_worker, name="service_worker"),
    # Web Views (Traditional Django Templates)
    path("", menu, name="menu"),
    path("dashboard/", dashboard, name="dashboard"),
    path("definicoes/", definicoes, name="definicoes"),
    path("pwa-diagnostico/", pwa_diagnostico, name="pwa_diagnostico"),
    path("itens/", listar_itens, name="itens"),
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
    path("criar-item/", criar_item, name="criar_item"),
    path("editar-item/<int:item_id>/", editar_item, name="editar_item"),
    path("apagar-item/<int:item_id>/", apagar_item, name="apagar_item"),
    path("editar-desejo/<int:desejo_id>/", editar_desejo, name="editar_desejo"),
    path("apagar-desejo/<int:desejo_id>/", apagar_desejo, name="apagar_desejo"),
    path("adicionar-compra/", adicionar_compra, name="adicionar_compra"),
    path("adicionar-consumivel/", adicionar_consumivel, name="adicionar_consumivel"),
    path("consumir/<int:consumivel_id>/", consumir_consumivel, name="consumir_consumivel"),
    path("repor/<int:consumivel_id>/", repor_consumivel, name="repor_consumivel"),
    path(
        "atualizar-quantidade/<int:consumivel_id>/",
        atualizar_quantidade_consumivel,
        name="atualizar_quantidade_consumivel",
    ),
    path("apagar-compra/<int:compra_id>/", apagar_compra, name="apagar_compra"),
]
