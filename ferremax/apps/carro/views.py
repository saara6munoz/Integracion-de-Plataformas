from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import CarroSerializer, CarroProductoSerializer
from .models import Carro, CarroProducto
from apps.producto.models import Producto

class CarroViewSet(viewsets.ModelViewSet):
    queryset = Carro.objects.all()
    serializer_class = CarroSerializer

@api_view(['POST'])
def agregar_producto_al_carro(request):
    try:
        codigo_producto = request.data.get('codigo_producto')
        cantidad = int(request.data.get('cantidad', 1))

        producto = get_object_or_404(Producto, codigo_producto=codigo_producto)

        if request.user.is_authenticated:
            usuario = request.user
            carro, creado = Carro.objects.get_or_create(usuario=usuario)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            carro, creado = Carro.objects.get_or_create(session_key=session_key)

        # Intenta obtener el CarroProducto existente para el producto
        carro_producto, creado = CarroProducto.objects.get_or_create(carro=carro, producto=producto)

        # Si el producto ya existe en el carro, actualiza la cantidad
        if not creado:
            carro_producto.cantidad += cantidad
            carro_producto.save()
        else:
            # Si es nuevo, simplemente asigna la cantidad proporcionada
            carro_producto.cantidad = cantidad
            carro_producto.save()

        mensaje = f'El producto {producto.nombre} se ha añadido al carro correctamente'
        return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({'error': 'El producto especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Similar cambio en la vista obtener_carro
@api_view(['GET'])
def obtener_carro(request):
    try:
        if request.user.is_authenticated:
            carro = Carro.objects.filter(usuario=request.user, pagado=False).first()
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            carro = Carro.objects.filter(session_key=session_key, pagado=False).first()

        if not carro:
            return Response({'carro_id': None, 'productos': [], 'total': 0}, status=status.HTTP_200_OK)

        carro_productos = CarroProducto.objects.filter(carro=carro).select_related('producto')

        productos = []
        total = 0
        for item in carro_productos:
            producto = item.producto
            producto_info = {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': item.cantidad
            }
            productos.append(producto_info)
            total += producto.precio * item.cantidad

        response_data = {
            'carro_id': carro.id,
            'productos': productos,
            'total': float(total)
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def eliminar_producto_del_carro(request, producto_id):
    try:
        if request.user.is_authenticated:
            carro = Carro.objects.get(usuario=request.user, pagado=False)
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response({'error': 'No hay carro para el usuario anónimo'}, status=status.HTTP_404_NOT_FOUND)
            carro = Carro.objects.get(session_key=session_key, pagado=False)

        producto = get_object_or_404(Producto, pk=producto_id)
        carro_producto = get_object_or_404(CarroProducto, carro=carro, producto=producto)

        carro_producto.delete()

        mensaje = f'El producto {producto.nombre} se ha eliminado del carro correctamente'
        return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
    except Carro.DoesNotExist:
        return Response({'error': 'No se encontró un carro activo'}, status=status.HTTP_404_NOT_FOUND)
    except CarroProducto.DoesNotExist:
        return Response({'error': 'El producto no está en el carro'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
