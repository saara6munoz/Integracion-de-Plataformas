from django.db import models
from apps.venta.models import Venta

class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    cantidad_pagada = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=[('Tarjeta', 'Tarjeta'), ('Efectivo', 'Efectivo'), ('Transferencia', 'Transferencia')])

    def __str__(self):
        return f'(self.metodo_pago ({self.metodo_pago})'
