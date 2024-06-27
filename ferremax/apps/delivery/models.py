from django.db import models
from apps.venta.models import Venta

class Delivery(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    direccion_envio = models.CharField(max_length=255)
    fecha_envio = models.DateTimeField()
    estado = models.CharField(max_length=50, choices=[('Pendiente', 'Pendiente'), ('Enviado', 'Enviado'), ('Entregado', 'Entregado')])

    def __str__(self):
        return f"Delivery {self.id} - Venta {self.venta.id}"
