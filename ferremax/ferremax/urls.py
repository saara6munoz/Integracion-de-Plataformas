from django.contrib import admin
from django.urls import path, include
from djoser import views as djoser_views
from apps.carro import views as carro_views
from apps.venta import views as ventas_views
from apps.producto import views as productos_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'productos', productos_views.ProductoViewSet)
router.register(r'carros', carro_views.CarroViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('carro/agregar/', carro_views.agregar_producto_al_carro, name='agregar_producto_al_carro'),
    path('carro/obtener/', carro_views.obtener_carro, name='obtener_carro'),
    path('carro/eliminar/<int:producto_id>/', carro_views.eliminar_producto_del_carro, name='eliminar_producto_del_carro'),
    path('ventas/pagar/', ventas_views.pagar_carro, name='pagar_carro'),
    path('admin/', admin.site.urls),
    path('ventas/', include('apps.venta.urls')),
    path('ventas/<int:pk>/', ventas_views.obtener_detalle_venta, name='venta-detail'),
    path('clientes/', include('apps.cliente.urls')),
    path('carro/agregar/', carro_views.agregar_producto_al_carro, name='agregar-producto-al-carro'),
    path('carro/obtener/', carro_views.obtener_carro, name='obtener-carro'),
    path('carro/eliminar/<int:producto_id>/', carro_views.eliminar_producto_del_carro, name='eliminar-producto-del-carro'),
    path('ventas/pagar/', ventas_views.pagar_carro, name='pagar-carro')
]

