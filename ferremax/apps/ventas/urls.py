from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_producto_al_carrito),
    path('pagar/', views.pagar_carrito),
    path('detalle/', views.obtener_carrito),
    path('eliminar-producto/<int:producto_id>/', views.eliminar_producto_del_carrito, name='eliminar_producto_del_carrito'),
]
