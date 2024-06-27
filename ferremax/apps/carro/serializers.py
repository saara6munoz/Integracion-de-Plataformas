from rest_framework import serializers
from .models import Carro, CarroProducto

class CarroProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarroProducto
        fields = ['producto', 'cantidad']

class CarroSerializer(serializers.ModelSerializer):
    productos = CarroProductoSerializer(many=True, source='carroproducto_set')

    class Meta:
        model = Carro
        fields = ['id', 'usuario', 'session_key', 'productos', 'pagado']
