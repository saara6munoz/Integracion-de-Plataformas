from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as ventas_views

router = DefaultRouter()
router.register(r'ventas', ventas_views.VentaViewSet, basename='venta')

urlpatterns = [
    path('', include(router.urls)),
]
