import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.producto.models import Producto
from apps.carro.models import Carro, CarroProducto
from apps.cliente.models import Cliente
from apps.venta.models import Venta
import logging

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_venta_con_productos():
    # Crear un producto para la venta
    producto = Producto.objects.create(
        codigo_producto='PROD123',
        marca='Marca Test',
        nombre='Producto de Prueba',
        precio='99.99',
        stock=10
    )

    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # Realizar la solicitud para agregar el producto al carro
    url_agregar_producto = reverse('agregar_producto_al_carro')
    print(url_agregar_producto)
    data_agregar_producto = {'codigo_producto': 'PROD123', 'cantidad': 1}
    response_agregar_producto = client.post(url_agregar_producto, data_agregar_producto, format='json')
    print(response_agregar_producto)
    logger.info("Inicio de la prueba ejemplo", response_agregar_producto)


    # Verificar el código de estado y otros resultados esperados
    assert response_agregar_producto.status_code == 200
    assert 'El producto Producto de Prueba se ha añadido al carro correctamente' in response_agregar_producto.data['mensaje']

    # Verificar que se haya creado correctamente el carro
    carros_creados = Carro.objects.filter(usuario=user)
    assert carros_creados.exists()

    # Verificar que el producto esté en el carro
    carro = carros_creados.first()
    assert carro.carroproducto_set.filter(producto=producto).exists()

    # Limpiar el usuario creado para la prueba
    user.delete()

@pytest.mark.django_db
def test_agregar_producto_al_carro():
    # Crear un producto inicial
    producto = Producto.objects.create(
        codigo_producto='PROD001',
        nombre='Producto de Prueba',
        precio='99.99',
        stock=10
    )

    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # URL para agregar producto al carro
    url_agregar_producto = reverse('agregar-producto-al-carro')

    # Datos para agregar producto al carro
    datos_agregar_producto = {
        'codigo_producto': producto.codigo_producto,
        'cantidad': 2
    }

    # Realizar la solicitud para agregar el producto al carro
    response = client.post(url_agregar_producto, datos_agregar_producto, format='json')

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 200

    # Verificar que el producto se haya agregado al carro correctamente
    carro = Carro.objects.get(usuario=user)
    assert CarroProducto.objects.filter(carro=carro, producto=producto).exists()

    # Limpiar el usuario creado para la prueba
    user.delete()

@pytest.mark.django_db
def test_eliminar_producto_del_carro():
    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # Crear un producto
    producto = Producto.objects.create(
        codigo_producto='PROD001',
        nombre='Producto a Eliminar',
        precio='49.99',
        stock=3
    )

    # Crear un carro y agregar el producto
    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # URL para eliminar el producto del carro
    url_eliminar_producto = reverse('eliminar-producto-del-carro', kwargs={'producto_id': producto.id})

    # Realizar la solicitud para eliminar el producto del carro
    response = client.delete(url_eliminar_producto)

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 200

    # Verificar que el producto se haya eliminado del carro correctamente
    assert not CarroProducto.objects.filter(carro=carro, producto=producto).exists()

    # Limpiar el usuario creado para la prueba
    user.delete()


@pytest.mark.django_db
def test_agregar_producto_y_verificar_cliente():
    # Crear un cliente (esto es opcional en el contexto actual, pero puede ser útil para futuras referencias)
    cliente = Cliente.objects.create(
        nombre='Cliente de Prueba',
        email='cliente@prueba.com',
        direccion='Calle Principal 123',
        telefono='123456789'
    )

    # Crear un producto
    producto = Producto.objects.create(
        codigo_producto='PROD123',
        marca='Marca Test',
        nombre='Producto de Prueba',
        precio='99.99',
        stock=10
    )

    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # Realizar la solicitud para agregar el producto al carro
    url_agregar_producto = reverse('agregar-producto-al-carro')
    data_agregar_producto = {'codigo_producto': 'PROD123', 'cantidad': 1}
    response_agregar_producto = client.post(url_agregar_producto, data_agregar_producto, format='json')

    # Verificar el código de estado y otros resultados esperados
    assert response_agregar_producto.status_code == 200
    assert 'El producto Producto de Prueba se ha añadido al carro correctamente' in response_agregar_producto.data['mensaje']

    # Verificar que se haya creado correctamente el carro
    carros_creados = Carro.objects.filter(usuario=user)
    assert carros_creados.exists()

    # Verificar que el producto esté en el carro
    carro = carros_creados.first()
    assert carro.carroproducto_set.filter(producto=producto).exists()

    # Verificar el estado del carro (opcional)
    assert carro.pagado == False  # El carro no debería estar pagado al añadir productos
    assert carro.session_key is not None  # La session_key debería estar generada

    # Limpiar el usuario y cliente creados para la prueba
    user.delete()
    cliente.delete()
