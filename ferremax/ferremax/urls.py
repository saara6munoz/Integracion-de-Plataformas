from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cliente/', include('apps.cliente.urls')), 
=======
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ventas/', include('apps.ventas.urls')),
>>>>>>> 7999f7d01ffa9c4cf2c23bd6df60defb8fefc1d4
]
