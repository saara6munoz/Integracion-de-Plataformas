from django.db import models
from ventas.models import Carrito

class Delivery(models.Model):
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE)
    fecha_delivery = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=100, default='Efectivo')  
    total = models.DecimalField(max_digits=10, decimal_places=2)
