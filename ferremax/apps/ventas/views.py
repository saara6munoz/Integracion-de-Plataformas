from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .serializer import CarritoSerializer, CarritoProductoSerializer
from .models import Carrito, CarritoProducto, Producto
#from finanzas.models import Pedido
#from finanzas.serializer import PedidoSerializer

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

@api_view(['POST'])
def agregar_producto_al_carrito(request):
    try:
        codigo_producto = request.data.get('codigo_producto') #parametros
        cantidad = int(request.data.get('cantidad', 1))  #parametros

        producto = get_object_or_404(Producto, codigo_producto=codigo_producto)

        if request.user.is_authenticated:
            usuario = request.user
            carrito, creado = Carrito.objects.get_or_create(usuario=usuario)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            carrito, creado = Carrito.objects.get_or_create(session_key=session_key)

        item, created = CarritoProducto.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item.cantidad += cantidad
            item.save()
        else:
            item.cantidad = cantidad
            item.save()

        mensaje = f'El producto {producto.nombre} se ha añadido al carrito correctamente'
        return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({'error': 'El producto especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def pagar_carrito(request):
    try:
        carrito_id = request.data['carrito_id']
        metodo_pago = request.data['metodo_pago']
    except KeyError:
        return Response({'error': 'carrito_id y metodo_pago son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        carrito = Carrito.objects.get(id=carrito_id, pagado=False)
    except Carrito.DoesNotExist:
        return Response({'error': 'Carrito no encontrado o ya pagado'}, status=status.HTTP_404_NOT_FOUND)

    # Actualizar el stock de los productos
    for item in carrito.carritoproducto_set.all():
        producto = item.producto
        if producto.stock < item.cantidad:
            return Response({'error': f'No hay suficiente stock para el producto {producto.nombre}'}, status=status.HTTP_400_BAD_REQUEST)
        producto.stock -= item.cantidad
        producto.save()

    total = sum(item.producto.precio * item.cantidad for item in carrito.carritoproducto_set.all())
  # pedido = Pedido.objects.create(carrito=carrito, metodo_pago=metodo_pago, total=total)

    carrito.pagado = True
    carrito.save()

    # Preparar la respuesta
    productos = []
    for item in carrito.carritoproducto_set.all():
        producto_info = {
            'nombre': item.producto.nombre,
            'precio': float(item.producto.precio),
            'metodo_pago': metodo_pago,
            'cantidad': item.cantidad
        }
        productos.append(producto_info)

    response_data = {
        'mensaje': 'Carro pagado y pedido finalizado correctamente.',
        'total': float(total),
        'carro': productos
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def obtener_carrito(request):
    try:
        if request.user.is_authenticated:
            carrito = Carrito.objects.filter(usuario=request.user, pagado=False).first()
        else:
            # Crear sesión si no existe
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            carrito = Carrito.objects.filter(session_key=session_key, pagado=False).first()

        if not carrito:
            return Response({'carrito_id': None, 'productos': [], 'total': 0}, status=status.HTTP_200_OK)

        carrito_productos = CarritoProducto.objects.filter(carrito=carrito).select_related('producto')

        productos = []
        total = 0
        for item in carrito_productos:
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
            'carrito_id': carrito.id,
            'productos': productos,
            'total': float(total)
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['DELETE'])
def eliminar_producto_del_carrito(request, producto_id):
    try:
        if request.user.is_authenticated:
            carrito = Carrito.objects.get(usuario=request.user, pagado=False)
        else:
            # Obtener carrito anónimo
            session_key = request.session.session_key
            if not session_key:
                return Response({'error': 'No hay carrito para el usuario anónimo'}, status=status.HTTP_404_NOT_FOUND)
            carrito = Carrito.objects.get(session_key=session_key, pagado=False)

        producto = get_object_or_404(Producto, pk=producto_id)
        carrito_producto = get_object_or_404(CarritoProducto, carrito=carrito, producto=producto)

        carrito_producto.delete()

        mensaje = f'El producto {producto.nombre} se ha eliminado del carrito correctamente'
        return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
    except Carrito.DoesNotExist:
        return Response({'error': 'No se encontró un carrito activo'}, status=status.HTTP_404_NOT_FOUND)
    except CarritoProducto.DoesNotExist:
        return Response({'error': 'El producto no está en el carrito'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)