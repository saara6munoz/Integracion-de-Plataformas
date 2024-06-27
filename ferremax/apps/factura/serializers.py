from rest_framework import serializers
from .models import Factura
from venta.models import Venta

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['id', 'carro', 'metodo_pago', 'total', 'fecha']

class facturaSerializer(serializers.ModelSerializer):
    venta = VentaSerializer()

    class Meta:
        model = Factura
        fields = ['id', 'venta', 'fecha_factura', 'total']
