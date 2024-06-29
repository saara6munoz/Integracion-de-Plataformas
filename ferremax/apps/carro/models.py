from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from apps.producto.models import Producto

class Carro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    pagado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generar una session_key si no se proporciona
        if not self.session_key:
            self.session_key = get_random_string(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Carro de {self.usuario.username}"


class CarroProducto(models.Model):
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, related_name='carroproducto_set')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.producto.nombre} en el carro {self.carro.id}"




