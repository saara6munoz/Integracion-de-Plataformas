from rest_framework import serializers
from .models import Inventario
from producto.serializer import ProductoSerializer

class InventarioSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = Inventario
        fields = ['id', 'producto', 'cantidad_disponible', 'ubicacion']
