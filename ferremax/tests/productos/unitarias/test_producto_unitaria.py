import pytest
from django.urls import reverse
from apps.producto.models import Producto
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


@pytest.mark.django_db  # Decorador necesario para pruebas que interactúan con la base de datos
def test_producto_crear():
    producto = Producto.objects.create(
                codigo_producto='XWTD3',
                marca='FHFD',
                nombre='Taladro',
                precio='50.99',  
                stock=2
    )

    assert producto.nombre == 'Taladro'


@pytest.mark.django_db
def test_producto_list_authenticated_with_djoser():
    client = APIClient()

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'mau',
        'password': 'mau456.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'mau',
        'password': 'mau456.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT: {token}')  

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Realizar la solicitud autenticada a la vista ProductoViewSet
    url = reverse('producto-list')
    response = client.get(url)

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 200
    assert len(response.data) == Producto.objects.count()

@pytest.mark.django_db
def test_producto_actualizar():
    # Crear un producto inicial
    producto = Producto.objects.create(
        codigo_producto='XWTD4',
        marca='FHFD',
        nombre='Taladro Viejo',
        precio='70.99',
        stock=5
    )

    # Crear un cliente de prueba
    client = APIClient()

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'userupdate',
        'password': 'update123.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'userupdate',
        'password': 'update123.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT para actualizar: {token}')

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # URL para actualizar el producto específico
    url = reverse('producto-detail', kwargs={'pk': producto.id})

    # Datos de actualización completos
    update_data = {
        'codigo_producto': producto.codigo_producto,
        'marca': producto.marca,
        'nombre': 'Taladro Nuevo',  # Campo a actualizar
        'precio': '75.99',  # Campo a actualizar
        'stock': producto.stock
    }

    # Realizar la solicitud de actualización
    response = client.put(url, update_data, format='json')

    # Verificar el código de estado y otros resultados esperados
    if response.status_code != 200:
        print(f'Error al actualizar el producto: {response.data}')  # Imprimir los detalles del error
    assert response.status_code == 200

    # Verificar que los datos se hayan actualizado correctamente
    producto.refresh_from_db()
    assert producto.nombre == 'Taladro Nuevo'
    assert str(producto.precio) == '75.99'


@pytest.mark.django_db
def test_producto_eliminar():
    # Crear un producto inicial
    producto = Producto.objects.create(
        codigo_producto='XWTD5',
        marca='FHFD',
        nombre='Taladro Para Eliminar',
        precio='60.99',
        stock=3
    )

    # Crear un cliente de prueba
    client = APIClient()

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'userdelete',
        'password': 'delete123.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')
    assert response.status_code == 201

    # Obtener el token de autenticación de Djoser para JWT
    response = client.post(reverse('jwt-create'), {
        'username': 'userdelete',
        'password': 'delete123.*test',
    }, format='json')
    assert response.status_code == 200

    token = response.data['access']
    print(f'Token JWT para eliminar: {token}')

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # URL para eliminar el producto específico
    url = reverse('producto-detail', kwargs={'pk': producto.id})

    # Realizar la solicitud de eliminación
    response = client.delete(url)

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 204  # Código de estado para eliminación exitosa

    # Verificar que el producto se haya eliminado de la base de datos
    with pytest.raises(Producto.DoesNotExist):
        Producto.objects.get(id=producto.id)

