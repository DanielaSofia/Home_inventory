from django.urls import path
from .views import dashboard
from rest_framework.routers import DefaultRouter
from .views import (
    DivisaoViewSet,
    ItemViewSet,
    editar_desejo,
    editar_item,
    apagar_item,
    apagar_desejo,
)
from django.urls import include

router = DefaultRouter()
router.register(r"divisoes", DivisaoViewSet)
router.register(r"itens", ItemViewSet)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/", include(router.urls)),
    path("editar-item/<int:item_id>/", editar_item, name="editar_item"),
    path("apagar-item/<int:item_id>/", apagar_item, name="apagar_item"),
    path("editar-desejo/<int:desejo_id>/", editar_desejo, name="editar_desejo"),
    path("apagar-desejo/<int:desejo_id>/", apagar_desejo, name="apagar_desejo"),
]
