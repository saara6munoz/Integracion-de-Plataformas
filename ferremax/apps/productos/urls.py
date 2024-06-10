from django.urls import path,include
from rest_framework import routers
from productos import views
# Define patrones de URL y los asocia con las funciones o clases de vista correspondientes que manejarán esas URLs

router = routers.DefaultRouter()
router.register(r'producto', views.ProductoViewSet)

urlpatterns = [
    path('', include(router.urls))
]