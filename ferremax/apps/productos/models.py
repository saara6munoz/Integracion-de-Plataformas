from django.db import models

class ProductoManager(models.Manager):
    def create_producto(self, codigo_producto, marca, nombre, precio, stock):
        # Crear un nuevo objeto Producto
        producto = self.create(
            codigo_producto=codigo_producto,
            marca=marca,
            nombre=nombre,
            precio=precio,
            stock=stock
        )
        return producto

class Producto(models.Model):
    codigo_producto = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)  

    objects = ProductoManager()  # Asociar el manager personalizado

    def __str__(self):
        return f'{self.nombre} ({self.codigo_producto})'
