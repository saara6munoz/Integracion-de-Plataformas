from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from djoser import views as djoser_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ventas/', include('apps.ventas.urls')),
    path('cliente/', include('apps.cliente.urls')), 
    path('users/auth/', include('djoser.urls.authtoken')),
    path('users/', include('djoser.urls')),
]

