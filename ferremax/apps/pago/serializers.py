from rest_framework import serializers
from .models import Pago
from venta.models import Venta

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['id', 'carro', 'metodo_pago', 'total', 'fecha']

class PagoSerializer(serializers.ModelSerializer):
    venta = VentaSerializer()

    class Meta:
        model = Pago
        fields = ['id', 'venta', 'fecha_pago', 'cantidad_pagada', 'metodo_pago']
