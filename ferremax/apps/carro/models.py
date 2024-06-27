from django.db import models
from django.contrib.auth.models import User
from apps.producto.models import Producto

class Carro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=50)
    pagado = models.BooleanField(default=False)

class CarroProducto(models.Model):
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, related_name='productos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Ejemplo de relación con Producto
    cantidad = models.IntegerField(default=1)
