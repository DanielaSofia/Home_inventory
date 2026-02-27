
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DivisaoViewSet, ItemViewSet

router = DefaultRouter()
router.register(r'divisoes', DivisaoViewSet)
router.register(r'itens', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
