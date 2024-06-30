import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.cliente.models import Cliente, ClienteUsuario
from apps.carro.models import Carro, CarroProducto
from apps.producto.models import Producto
from apps.venta.models import Venta
from rest_framework.test import APIClient
from rest_framework import status
from django.db import transaction

@pytest.fixture
def api_client(cliente):
    client = APIClient()
    user = cliente.clienteusuario.user
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def cliente():
    cliente = Cliente.objects.create(nombre="Cliente Test")
    user = User.objects.create(username="clientetest")
    ClienteUsuario.objects.create(cliente=cliente, user=user)
    return cliente

@pytest.fixture
def productos():
    producto1 = Producto.objects.create(nombre="Producto 1", precio=10.0)  # Asegura que el precio esté definido
    producto2 = Producto.objects.create(nombre="Producto 2", precio=15.0)  # Asegura que el precio esté definido
    return [producto1, producto2]

@pytest.fixture
def producto():
    return Producto.objects.create(nombre='Producto de Prueba', precio=99.99, stock=10)

@pytest.mark.django_db
def test_crear_carro_para_cliente_con_productos(api_client, cliente, productos):
    # Obtener el cliente y su usuario asociado a través de ClienteUsuario
    cliente_usuario = ClienteUsuario.objects.get(cliente=cliente)
    usuario = cliente_usuario.user

    # Crear un carro asociado al usuario
    carro_data = {
        'usuario': usuario.id,
        'productos': [{'producto': p.id, 'cantidad': 1} for p in productos]
    }
    url = reverse('carro-list')  # Asegúrate de que 'carro-list' sea la URL correcta para crear carros
    response = api_client.post(url, carro_data, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_asociar_venta_a_carro_existente(api_client, cliente, productos):
    # Obtener el usuario asociado al cliente a través de ClienteUsuario
    cliente_usuario = ClienteUsuario.objects.get(cliente=cliente)
    usuario = cliente_usuario.user

    # Crear un carro asociado al cliente
    carro = Carro.objects.create(usuario=usuario)
    for producto in productos:
        CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # Crear una venta asociada al carro
    venta_data = {
        'carro': carro.id,  # Enviar solo el id del carro
        'metodo_pago': 'Tarjeta de crédito',  # Ajusta según el método de pago deseado
        'total': sum(p.precio for p in productos),  # Calcula el total correctamente
    }

    response_venta = api_client.post(reverse('venta-list'), venta_data, format='json')
    assert response_venta.status_code == 201



@pytest.mark.django_db
def test_actualizar_productos_en_carro(api_client, cliente, producto):
    # Autenticar cliente
    user = cliente.clienteusuario.user
    api_client.force_authenticate(user=user)

    # Crear un carro asociado al cliente
    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # Obtener la URL del detalle del carro
    carro_url = reverse('carro-detail', args=[carro.id])

    # Crear un nuevo producto para agregar al carro
    nuevo_producto = Producto.objects.create(nombre='Nuevo Producto', precio=50.0)

    # Datos de actualización del carro
    carro_data = {
        'productos': [
            {'producto': nuevo_producto.id, 'cantidad': 1}
        ]
    }

    # Realizar la solicitud PATCH para actualizar el carro
    response = api_client.patch(carro_url, carro_data, format='json')

    # Verificar el código de estado esperado
    assert response.status_code == status.HTTP_200_OK

    # Refrescar el objeto carro desde la base de datos después de la actualización
    carro.refresh_from_db()

    # Verificar que el carro ahora tenga 2 productos (el inicial y el nuevo)
    assert carro.carroproducto_set.count() == 2


@pytest.mark.django_db
def test_eliminar_carro_y_verificar_integridad_productos(api_client, cliente, productos):
    # Obtener el usuario asociado al cliente a través de ClienteUsuario
    cliente_usuario = ClienteUsuario.objects.get(cliente=cliente)
    usuario = cliente_usuario.user
    # Crear un carro asociado al cliente con algunos productos
    carro = Carro.objects.create(usuario=usuario)
    for producto in productos:
        CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # Verificar que los productos están asociados al carro
    assert carro.carroproducto_set.count() == len(productos)

    # Eliminar el carro
    response_delete = api_client.delete(reverse('carro-detail', args=[carro.id]))
    assert response_delete.status_code == 204  # No Content

    # Verificar que el carro ha sido eliminado
    with pytest.raises(Carro.DoesNotExist):
        Carro.objects.get(id=carro.id)

    # Verificar que las relaciones de CarroProducto se han eliminado
    assert CarroProducto.objects.filter(carro=carro).count() == 0

    # Verificar que los productos originales no han sido eliminados
    for producto in productos:
        assert Producto.objects.filter(id=producto.id).exists()
