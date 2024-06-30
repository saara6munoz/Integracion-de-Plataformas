from rest_framework import serializers
from .models import Venta, Carro

class VentaSerializer(serializers.ModelSerializer):
    carro = serializers.PrimaryKeyRelatedField(queryset=Carro.objects.all())

    class Meta:
        model = Venta
        fields = '__all__'

    def create(self, validated_data):
        carro_id = self.validated_data['carro'].id  # Obtener el ID del carro
        try:
            carro_instance = Carro.objects.get(id=carro_id)
        except Carro.DoesNotExist:
            raise serializers.ValidationError("Carro no encontrado")

        validated_data['carro'] = carro_instance

        venta = Venta.objects.create(**validated_data)
        return venta

