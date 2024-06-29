from django.db import models
from apps.cliente.models import Cliente
from apps.carro.models import Carro

class Venta(models.Model):
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, related_name='ventas')
    metodo_pago = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id} - Carro {self.carro.id}"
