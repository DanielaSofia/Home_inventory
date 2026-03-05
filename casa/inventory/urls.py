from django.urls import path
from .views import dashboard
from rest_framework.routers import DefaultRouter
from .views import DivisaoViewSet, ItemViewSet
from django.urls import include

router = DefaultRouter()
router.register(r"divisoes", DivisaoViewSet)
router.register(r"itens", ItemViewSet)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/", include(router.urls)),
]
