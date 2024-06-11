from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),  # Rutas para registro y login
    path('auth/', include('djoser.urls.authtoken')),  # Rutas para manejo de tokens
    path('', include(router.urls)),
]
