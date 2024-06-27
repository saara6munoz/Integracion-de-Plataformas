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
                precio='50.99',  # Asegúrate de usar un formato numérico para el campo Decimal
                stock=2
    )

    assert producto.nombre == 'Taladro'


@pytest.mark.django_db
def test_producto_list_authenticated_with_djoser():
    # Crear un cliente de prueba para hacer solicitudes HTTP
    client = APIClient()

    # Registrar un usuario utilizando Djoser
    user_data = {
        'username': 'mau',
        'password': 'mau456.*test',
    }
    response = client.post(reverse('user-list'), user_data, format='json')  # Ajustar según la configuración de Djoser

    assert response.status_code == 201  # Asumiendo que el usuario se crea correctamente

    # Obtener el token de autenticación de Djoser
    response = client.post(reverse('token_obtain_pair'), {
        'username': 'mau',
        'password': 'mau456.*test',
    }, format='json')

    assert response.status_code == 200
    token = response.data['access']

    # Configurar la autenticación en la solicitud con el token de Djoser
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Realizar la solicitud autenticada a la vista ProductoViewSet
    url = reverse('producto-list')
    response = client.get(url)

    # Verificar el código de estado y otros resultados esperados
    assert response.status_code == 200
    assert len(response.data) == Producto.objects.count()
