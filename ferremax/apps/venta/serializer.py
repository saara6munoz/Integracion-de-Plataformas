from rest_framework import serializers
from .models import Venta
from apps.carro.serializers import CarroSerializer  

class VentaSerializer(serializers.ModelSerializer):
    carro = CarroSerializer()  

    class Meta:
        model = Venta
        fields = ['id', 'carro', 'metodo_pago', 'total', 'fecha_venta']
