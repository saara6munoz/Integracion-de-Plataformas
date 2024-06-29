from rest_framework import serializers
from .models import Carro, CarroProducto
from apps.producto.models import Producto

class CarroProductoSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = CarroProducto
        fields = ('producto', 'cantidad')

class CarroSerializer(serializers.ModelSerializer):
    productos = CarroProductoSerializer(many=True, source='carroproducto_set', required=False)

    class Meta:
        model = Carro
        fields = ('id', 'usuario', 'productos')

    def create(self, validated_data):
        # Extraer datos de productos
        productos_data = validated_data.pop('carroproducto_set', [])
        
        # Crear el Carro
        carro = Carro.objects.create(**validated_data)
        
        # Crear los CarroProducto asociados
        for producto_data in productos_data:
            CarroProducto.objects.create(carro=carro, **producto_data)
        
        return carro

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        productos = CarroProducto.objects.filter(carro=instance)
        representation['productos'] = CarroProductoSerializer(productos, many=True).data
        return representation
