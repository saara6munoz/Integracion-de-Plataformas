from django.db import models
from apps.productos.models import Producto

class Carrito(models.Model):
    usuario = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    pagado = models.BooleanField(default=False)

class CarritoProducto(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)  # Establecer 1 como valor por defecto

    def save(self, *args, **kwargs):
        # Asegurarse de que la cantidad no sea menor que 1 al guardar
        if self.cantidad < 1:
            self.cantidad = 1
        super().save(*args, **kwargs)

