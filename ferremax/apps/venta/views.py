from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Venta
from apps.producto.models import Producto
from apps.carro.models import Carro, CarroProducto
from .serializer import VentaSerializer

@api_view(['POST'])
def pagar_carro(request):
    try:
        carro_id = request.data['carro_id']
        metodo_pago = request.data['metodo_pago']
    except KeyError:
        return Response({'error': 'carro_id y metodo_pago son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        carro = Carro.objects.get(id=carro_id, pagado=False)
    except Carro.DoesNotExist:
        return Response({'error': 'Carro no encontrado o ya pagado'}, status=status.HTTP_404_NOT_FOUND)

    for item in carro.carroproducto_set.all():
        producto = item.producto
        if producto.stock < item.cantidad:
            return Response({'error': f'No hay suficiente stock para el producto {producto.nombre}'}, status=status.HTTP_400_BAD_REQUEST)
        producto.stock -= item.cantidad
        producto.save()

    total = sum(item.producto.precio * item.cantidad for item in carro.carroproducto_set.all())
    venta = Venta.objects.create(carro=carro, metodo_pago=metodo_pago, total=total)

    carro.pagado = True
    carro.save()

    productos = []
    for item in carro.carroproducto_set.all():
        producto_info = {
            'nombre': item.producto.nombre,
            'precio': float(item.producto.precio),
            'metodo_pago': metodo_pago,
            'cantidad': item.cantidad
        }
        productos.append(producto_info)

    response_data = {
        'mensaje': 'Carro pagado y venta finalizada correctamente.',
        'total': float(total),
        'carro': productos
    }

    return Response(response_data, status=status.HTTP_200_OK)
