from rest_framework import serializers
from .models import Carrito, CarritoProducto

class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = '__all__'

class CarritoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoProducto
        fields = '__all__'
