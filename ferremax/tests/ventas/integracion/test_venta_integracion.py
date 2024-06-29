import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.producto.models import Producto
from apps.carro.models import Carro
from apps.cliente.models import Cliente
from apps.venta.models import Venta

@pytest.mark.django_db
def test_venta_con_cliente():
    # Crear un cliente para la venta
    cliente = Cliente.objects.create(
        nombre='Cliente de Prueba',
        email='cliente@prueba.com',
        direccion='Calle Principal 123',
        telefono='123456789'
    )

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

    # Realizar la solicitud para pagar el carro (simulación)
    url_pagar_carro = reverse('pagar-carro')
    data_pagar_carro = {'carro_id': carro.id, 'metodo_pago': 'tarjeta'}  # Asegúrate de enviar los datos requeridos
    response_pagar_carro = client.post(url_pagar_carro, data_pagar_carro, format='json')

    # Verificar el código de estado y otros resultados esperados
    assert response_pagar_carro.status_code == 200
    assert 'Carro pagado y venta finalizada correctamente.' in response_pagar_carro.data['mensaje']

    # Verificar que se haya creado correctamente la venta asociada al usuario a través de su carro
    ventas_usuario = Venta.objects.filter(carro__usuario=user)
    assert ventas_usuario.exists()


    # Limpiar el usuario creado para la prueba
    user.delete()