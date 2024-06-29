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
        print(f"Carro ID recibido: {carro_id}, Método de pago: {metodo_pago}")

    except KeyError:
        return Response({'error': 'carro_id y metodo_pago son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        carro = Carro.objects.get(id=carro_id, pagado=False)
        print(f"Carro encontrado: {carro}")
    except Carro.DoesNotExist:
        return Response({'error': 'Carro no encontrado o ya pagado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Validar y actualizar el stock de productos
        for item in carro.carroproducto_set.all():
            producto = item.producto
            if producto.stock < item.cantidad:
                return Response({'error': f'No hay suficiente stock para el producto {producto.nombre}'}, status=status.HTTP_400_BAD_REQUEST)
            producto.stock -= item.cantidad
            producto.save()

        # Calcular el total de la venta
        total = sum(item.producto.precio * item.cantidad for item in carro.carroproducto_set.all())

        # Crear la venta y marcar el carro como pagado
        venta = Venta.objects.create(carro=carro, metodo_pago=metodo_pago, total=total)
        carro.pagado = True
        carro.save()

        # Preparar los datos de respuesta
        productos = []
        for item in carro.carroproducto_set.all():
            producto_info = {
                'nombre': item.producto.nombre,
                'precio': float(item.producto.precio),
                'cantidad': item.cantidad
            }
            productos.append(producto_info)

        response_data = {
            'mensaje': 'Carro pagado y venta finalizada correctamente.',
            'total': float(total),
            'productos': productos
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
