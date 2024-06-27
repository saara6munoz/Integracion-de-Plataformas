from django.db import models
from apps.venta.models import Venta

class Factura(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    fecha_factura = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Factura {self.id} - Venta {self.venta.id}"
