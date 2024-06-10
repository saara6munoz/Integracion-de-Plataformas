from django.contrib import admin
from .models import Producto

# Hacen que los modelos estén disponibles en la interfaz de administración.

admin.site.register(Producto)