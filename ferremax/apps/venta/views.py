from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Venta
from apps.producto.models import Producto
from apps.carro.models import Carro, CarroProducto
from .serializer import VentaSerializer
from rest_framework import viewsets

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def create(self, request):
        serializer = VentaSerializer(data=request.data)
        if serializer.is_valid():
            venta = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    
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

@api_view(['GET'])
def obtener_detalle_venta(request, pk):
    try:
        venta = Venta.objects.get(pk=pk)
    except Venta.DoesNotExist:
        return Response({'error': 'Venta no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    # Aquí decides cómo quieres serializar el carro
    if request.query_params.get('simple', False):
        # Si se especifica 'simple=true' en los parámetros de consulta, devuelve solo el ID del carro
        carro_id = venta.carro.id
        return Response({'carro_id': carro_id}, status=status.HTTP_200_OK)
    else:
        # De lo contrario, devuelve el objeto serializado completo
        serializer = VentaSerializer(venta)
        return Response(serializer.data, status=status.HTTP_200_OK)
