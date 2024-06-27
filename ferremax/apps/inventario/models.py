from django.db import models
from apps.producto.models import Producto

class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_disponible = models.IntegerField()
    ubicacion = models.CharField(max_length=100)

    def __str__(self):
        return f"Inventario de {self.producto.nombre}"
