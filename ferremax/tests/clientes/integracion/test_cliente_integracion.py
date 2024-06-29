import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.producto.models import Producto
from apps.carro.models import Carro, CarroProducto
from apps.cliente.models import Cliente
from apps.venta.models import Venta
import logging

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(api_client):
    # Crear un usuario
    user = User.objects.create_user(username='testuser', password='testpass123')
    # Obtener el token JWT para el usuario
    response = api_client.post(reverse('jwt-create'), {'username': 'testuser', 'password': 'testpass123'}, format='json')
    assert response.status_code == 200
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    return user

@pytest.mark.django_db
def test_crear_cliente_y_asociar_con_carro(api_client, user):
    # Crear un cliente asociado al usuario
    cliente_data = {
        'nombre': 'Cliente Test',
        'email': 'cliente@test.com',
        'direccion': 'Calle Principal 456',
        'telefono': '987654321'
    }
    response_cliente = api_client.post(reverse('cliente-list'), cliente_data, format='json')
    assert response_cliente.status_code == 201

    # Verificar la creación del cliente
    cliente_id = response_cliente.data['id']
    cliente = Cliente.objects.get(id=cliente_id)
    assert cliente.nombre == 'Cliente Test'

    # Crear un carro asociado al usuario, incluyendo un campo productos vacío
    carro_data = {
        'usuario': user.id,
        'productos': []  # Puede ser una lista vacía o con productos
    }
    response_carro = api_client.post(reverse('carro-list'), carro_data, format='json')

    # Imprimir la respuesta para depuración
    print(response_carro.status_code)
    print(response_carro.data)  # Esto mostrará los detalles del error

    assert response_carro.status_code == 201




@pytest.mark.django_db
def test_actualizar_cliente_y_verificar_integracion_ventas(api_client, user):
    # Crear un cliente asociado al usuario
    cliente = Cliente.objects.create(
        nombre='Cliente Inicial',
        email='cliente@inicial.com',
        direccion='Calle Inicial 123',
        telefono='123456789'
    )

    # Crear un carro asociado al usuario
    carro = Carro.objects.create(usuario=user)

    # Crear una venta asociada al carro
    venta = Venta.objects.create(
        carro=carro,
        metodo_pago='Efectivo',
        total=100.00
    )

    # Actualizar el cliente y verificar integración con la venta
    update_data = {
        'nombre': 'Cliente Actualizado',
        'direccion': 'Calle Actualizada 456'
    }
    url_cliente = reverse('cliente-detail', args=[cliente.id])
    response_update = api_client.patch(url_cliente, update_data, format='json')
    assert response_update.status_code == 200

    # Verificar que la venta refleje los cambios en el cliente
    cliente.refresh_from_db()
    venta_actualizada = Venta.objects.get(id=venta.id)
    assert cliente.nombre == 'Cliente Actualizado'

@pytest.mark.django_db
def test_eliminar_cliente_y_verificar_eliminacion_productos_ventas(api_client, user):
    # Crear un cliente inicialmente
    cliente = Cliente.objects.create(
        nombre='Cliente a Eliminar',
        email='cliente@eliminar.com',
        direccion='Calle Eliminación 123',
        telefono='987654321'
    )

    # Crear productos y ventas asociadas al cliente
    producto = Producto.objects.create(
        codigo_producto='PROD123',
        marca='Marca Test',
        nombre='Producto de Prueba',
        precio='99.99',
        stock=10
    )

    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto, cantidad=2)  # Relación ManyToMany

    venta = Venta.objects.create(
        carro=carro,
        metodo_pago='Tarjeta',
        total=200.00
    )

    # Eliminar el cliente y verificar eliminación de productos y ventas
    url_cliente = reverse('cliente-detail', args=[cliente.id])
    response_delete = api_client.delete(url_cliente)
    assert response_delete.status_code == 204

    # Verificar que los productos no sean eliminados (porque no están directamente relacionados con el cliente)
    assert Producto.objects.filter(nombre='Producto de Prueba').exists()

    # Verificar que las ventas aún existan porque eliminar un cliente no debería eliminar ventas a menos que se especifique
    assert Venta.objects.filter(carro=carro).exists()



@pytest.mark.django_db
def test_listar_clientes_y_verificar_integracion_productos_carros(api_client, user):
    # Crear varios clientes en la base de datos
    cliente1 = Cliente.objects.create(
        nombre='Cliente 1',
        email='cliente1@test.com',
        direccion='Calle Principal 123',
        telefono='111222333'
    )
    cliente2 = Cliente.objects.create(
        nombre='Cliente 2',
        email='cliente2@test.com',
        direccion='Calle Secundaria 456',
        telefono='444555666'
    )

    # Crear productos y asociarlos a carros
    producto1 = Producto.objects.create(
        codigo_producto='PROD1',
        marca='Marca 1',
        nombre='Producto 1',
        precio='50.00',
        stock=5
    )
    carro1 = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro1, producto=producto1, cantidad=2)

    producto2 = Producto.objects.create(
        codigo_producto='PROD2',
        marca='Marca 2',
        nombre='Producto 2',
        precio='75.00',
        stock=10
    )
    carro2 = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro2, producto=producto2, cantidad=3)

    # Realizar la solicitud para obtener la lista de clientes
    url_clientes = reverse('cliente-list')
    response_listado = api_client.get(url_clientes)
    assert response_listado.status_code == 200

    # Verificar que la respuesta contenga detalles correctos de productos y carros asociados
    assert len(response_listado.data) == 2
    assert response_listado.data[0]['nombre'] == 'Cliente 1'
    assert response_listado.data[1]['nombre'] == 'Cliente 2'
