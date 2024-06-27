from django.db import models
from apps.cliente.models import Cliente  # Importa el modelo Cliente desde su aplicación correspondiente
from apps.producto.models import Producto  # Importa el modelo Producto desde su aplicación correspondiente

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre}"
