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

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('carroproducto_set', None)
        instance.usuario = validated_data.get('usuario', instance.usuario)
        instance.save()

        if productos_data is not None:
            # Crear un diccionario de los productos existentes en el carrito
            existing_productos = {cp.producto.id: cp for cp in instance.carroproducto_set.all()}
            
            for producto_data in productos_data:
                producto = producto_data.get('producto')
                cantidad = producto_data.get('cantidad', 1)

                if producto.id in existing_productos:
                    # Actualizar la cantidad si el producto ya está en el carrito
                    existing_productos[producto.id].cantidad += cantidad
                    existing_productos[producto.id].save()
                else:
                    # Crear un nuevo CarroProducto si el producto no está en el carrito
                    CarroProducto.objects.create(carro=instance, producto=producto, cantidad=cantidad)

        return instance