import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.carro.models import Carro, CarroProducto
from apps.producto.models import Producto

@pytest.mark.django_db
def test_agregar_producto_al_carro():
    """
    Prueba para agregar un producto al carro de un usuario autenticado.
    """
    client = APIClient()

    # Crear usuario y producto de prueba
    user = User.objects.create_user(username='testuser', password='testpassword')
    producto = Producto.objects.create(nombre='Producto Test', precio=100.00, codigo_producto='12345')

    # Autenticar al usuario
    client.login(username='testuser', password='testpassword')

    # Realizar la solicitud de agregar producto al carro
    response = client.post(reverse('agregar_producto_al_carro'), {'codigo_producto': '12345', 'cantidad': 2})

    # Verificar que el producto se haya añadido correctamente al carro
    assert response.status_code == status.HTTP_200_OK
    assert 'El producto Producto Test se ha añadido al carro correctamente' in response.data['mensaje']

    # Verificar que el producto esté en el carro con la cantidad correcta
    carro = Carro.objects.get(usuario=user)
    assert carro.carroproducto_set.count() == 1


@pytest.mark.django_db
def test_obtener_carro():
    """
    Prueba para obtener el carro de un usuario autenticado.
    """
    client = APIClient()

    # Crear usuario, carro y producto
    user = User.objects.create_user(username='testuser', password='testpassword')
    producto = Producto.objects.create(nombre='Producto Test', precio=100.00, codigo_producto='12345')
    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto, cantidad=3)

    # Autenticar al usuario
    client.login(username='testuser', password='testpassword')

    # Realizar la solicitud para obtener el carro
    response = client.get(reverse('obtener_carro'))

    # Verificar que la respuesta contenga el carro y sus productos
    assert response.status_code == status.HTTP_200_OK
    assert response.data['carro_id'] == carro.id
    assert len(response.data['productos']) == 1
    assert response.data['productos'][0]['cantidad'] == 3
    assert response.data['total'] == producto.precio * 3

@pytest.mark.django_db
def test_eliminar_producto_del_carro():
    """
    Prueba para eliminar un producto del carro de un usuario autenticado.
    """
    client = APIClient()

    # Crear usuario, carro y producto
    user = User.objects.create_user(username='testuser', password='testpassword')
    producto = Producto.objects.create(nombre='Producto Test', precio=100.00, codigo_producto='12345')
    carro = Carro.objects.create(usuario=user)
    CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # Autenticar al usuario
    client.login(username='testuser', password='testpassword')

    # Realizar la solicitud para eliminar el producto del carro
    response = client.delete(reverse('eliminar_producto_del_carro', args=[producto.id]))

    # Verificar que el producto se haya eliminado correctamente del carro
    assert response.status_code == status.HTTP_200_OK
    assert 'El producto Producto Test se ha eliminado del carro correctamente' in response.data['mensaje']
    assert carro.carroproducto_set.count() == 0

@pytest.mark.django_db
def test_carro_viewset_list():
    """
    Prueba para verificar la lista de carros a través del viewset.
    """
    client = APIClient()

    # Crear usuario y carros
    user = User.objects.create_user(username='testuser', password='testpassword')
    Carro.objects.create(usuario=user)
    Carro.objects.create(usuario=user)

    # Autenticar al usuario
    client.login(username='testuser', password='testpassword')

    # Realizar la solicitud para listar los carros
    response = client.get(reverse('carro-list'))

    # Verificar que la lista de carros obtenida sea la esperada
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
