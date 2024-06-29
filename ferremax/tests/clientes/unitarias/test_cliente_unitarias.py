import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.cliente.models import Cliente
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

@pytest.mark.django_db  # Decorador necesario para pruebas que interactúan con la base de datos
def test_cliente_crear():
    client = APIClient()

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'user_cliente',
        'password': 'cliente123.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'user_cliente',
        'password': 'cliente123.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT para crear cliente: {token}')

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Datos del nuevo cliente
    cliente_data = {
        'nombre': 'Cliente Prueba',
        'direccion': 'Calle Falsa 123',
        'telefono': '123456789',
        'email': 'cliente@prueba.com'
    }

    # Realizar la solicitud de creación
    url = reverse('cliente-list')
    response = client.post(url, cliente_data, format='json')

    # Verificar el código de estado y la creación correcta del cliente
    assert response.status_code == 201
    assert response.data['nombre'] == 'Cliente Prueba'

@pytest.mark.django_db
def test_cliente_list_authenticated_with_djoser():
    client = APIClient()

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'user_cliente_list',
        'password': 'list123.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'user_cliente_list',
        'password': 'list123.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT para listar clientes: {token}')

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Crear algunos clientes para listar
    Cliente.objects.create(nombre='Cliente 1', direccion='Direccion 1', telefono='111111', email='cliente1@test.com')
    Cliente.objects.create(nombre='Cliente 2', direccion='Direccion 2', telefono='222222', email='cliente2@test.com')

    # Realizar la solicitud de listado
    url = reverse('cliente-list')
    response = client.get(url)

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 200
    assert len(response.data) == 2  # Debe haber dos clientes

@pytest.mark.django_db
def test_cliente_actualizar():
    client = APIClient()

    # Crear un cliente inicial
    cliente = Cliente.objects.create(
        nombre='Cliente Viejo',
        direccion='Direccion Vieja',
        telefono='333333',
        email='clienteviejo@test.com'
    )

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'user_cliente_update',
        'password': 'update123.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'user_cliente_update',
        'password': 'update123.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT para actualizar cliente: {token}')

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # URL para actualizar el cliente específico
    url = reverse('cliente-detail', kwargs={'pk': cliente.id})

    # Datos de actualización
    update_data = {
        'nombre': 'Cliente Nuevo',
        'direccion': 'Direccion Nueva',
        'telefono': '444444',
        'email': 'clientenuevo@test.com'
    }

    # Realizar la solicitud de actualización
    response = client.put(url, update_data, format='json')

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 200

    # Verificar que los datos se hayan actualizado correctamente
    cliente.refresh_from_db()
    assert cliente.nombre == 'Cliente Nuevo'
    assert cliente.direccion == 'Direccion Nueva'
    assert cliente.telefono == '444444'
    assert cliente.email == 'clientenuevo@test.com'

@pytest.mark.django_db
def test_cliente_eliminar():
    client = APIClient()

    # Crear un cliente inicial
    cliente = Cliente.objects.create(
        nombre='Cliente a Eliminar',
        direccion='Direccion Eliminar',
        telefono='555555',
        email='clienteaeliminar@test.com'
    )

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'user_cliente_delete',
        'password': 'delete123.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'user_cliente_delete',
        'password': 'delete123.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT para eliminar cliente: {token}')

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # URL para eliminar el cliente específico
    url = reverse('cliente-detail', kwargs={'pk': cliente.id})

    # Realizar la solicitud de eliminación
    response = client.delete(url)

    # Verificar el código de estado
    assert response.status_code == 204

    # Verificar que el cliente ya no existe en la base de datos
    with pytest.raises(Cliente.DoesNotExist):
        Cliente.objects.get(pk=cliente.id)
