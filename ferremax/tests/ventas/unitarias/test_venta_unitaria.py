import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.cliente.models import Cliente
from apps.carro.models import Carro, CarroProducto
from apps.producto.models import Producto
from apps.venta.models import Venta
from apps.venta.serializer import VentaSerializer

@pytest.mark.django_db
def test_pago_carro_exitoso():
    # Crear usuario y productos de prueba
    user = User.objects.create_user(username='testuser', password='testpassword')
    producto1 = Producto.objects.create(nombre='Producto Test 1', precio=100.00, stock=10, codigo_producto='12345')
    producto2 = Producto.objects.create(nombre='Producto Test 2', precio=50.00, stock=5, codigo_producto='67890')

    # Crear carro con productos
    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto1, cantidad=2)
    CarroProducto.objects.create(carro=carro, producto=producto2, cantidad=3)

    # Autenticar al usuario y pagar el carro
    client = APIClient()
    client.login(username='testuser', password='testpassword')
    url = reverse('pagar_carro')
    data = {'carro_id': carro.id, 'metodo_pago': 'tarjeta'}
    response = client.post(url, data, format='json')

    # Verificar el estado de la respuesta y la creación de la venta
    assert response.status_code == status.HTTP_200_OK
    assert 'Carro pagado y venta finalizada correctamente.' in response.data['mensaje']

    # Obtener el carro actualizado desde la base de datos
    carro_actualizado = Carro.objects.get(id=carro.id)

    # Verificar que el carro ahora esté marcado como pagado
    assert carro_actualizado.pagado

    # Verificar que existe una venta asociada al carro
    assert Venta.objects.filter(carro=carro).exists()


@pytest.mark.django_db
def test_pago_carro_sin_stock():
    # Crear usuario y productos de prueba
    user = User.objects.create_user(username='testuser', password='testpassword')
    producto1 = Producto.objects.create(nombre='Producto Test 1', precio=100.00, stock=2, codigo_producto='12345')

    # Crear carro con productos
    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto1, cantidad=3)

    # Autenticar al usuario y tratar de pagar el carro
    client = APIClient()
    client.login(username='testuser', password='testpassword')
    url = reverse('pagar_carro')
    data = {'carro_id': carro.id, 'metodo_pago': 'tarjeta'}
    response = client.post(url, data, format='json')

    # Verificar el estado de la respuesta y que el carro no se haya marcado como pagado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'No hay suficiente stock para el producto' in response.data['error']
    assert not carro.pagado

@pytest.mark.django_db
def test_pago_carro_inexistente():
    # Crear usuario
    user = User.objects.create_user(username='testuser', password='testpassword')

    # Autenticar al usuario y tratar de pagar un carro inexistente
    client = APIClient()
    client.login(username='testuser', password='testpassword')
    url = reverse('pagar_carro')
    data = {'carro_id': 999, 'metodo_pago': 'tarjeta'}
    response = client.post(url, data, format='json')

    # Verificar el estado de la respuesta y el mensaje de error
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Carro no encontrado o ya pagado' in response.data['error']

@pytest.mark.django_db
def test_venta_serializacion():
    # Crear un carro de prueba
    user = User.objects.create_user(username='testuser', password='testpassword')
    carro = Carro.objects.create(usuario=user)

    # Crear una venta de prueba asociada al carro
    venta = Venta.objects.create(carro=carro, metodo_pago='tarjeta', total=200.00)

    # Serializar la venta y verificar los datos
    serializer = VentaSerializer(instance=venta)
    assert serializer.data['carro']['id'] == carro.id
    assert serializer.data['metodo_pago'] == 'tarjeta'
    assert serializer.data['total'] == '200.00'


