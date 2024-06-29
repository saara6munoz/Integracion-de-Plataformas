from django.urls import path, include
from rest_framework import routers
from apps.cliente import views

router = routers.DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),  # Incluye las URLs de tu API RESTful
    path('api/v1/auth/', include('djoser.urls')),  # URLs de Djoser para autenticación
    path('api/v1/auth/', include('djoser.urls.authtoken')),  # URLs de Djoser para token de autenticación
    path('api/v1/auth/', include('djoser.urls.jwt')),  # URLs de Djoser para JWT
]
