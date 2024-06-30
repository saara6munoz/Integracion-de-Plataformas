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


@pytest.mark.django_db
def test_venta_con_varios_productos():
    # Crear productos para la venta
    producto1 = Producto.objects.create(
        codigo_producto='PROD1',
        marca='Marca 1',
        nombre='Producto 1',
        precio='50.00',
        stock=20
    )
    producto2 = Producto.objects.create(
        codigo_producto='PROD2',
        marca='Marca 2',
        nombre='Producto 2',
        precio='30.00',
        stock=15
    )

    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # Agregar productos al carro
    url_agregar_producto = reverse('agregar-producto-al-carro')
    data_agregar_producto1 = {'codigo_producto': 'PROD1', 'cantidad': 2}
    data_agregar_producto2 = {'codigo_producto': 'PROD2', 'cantidad': 1}
    client.post(url_agregar_producto, data_agregar_producto1, format='json')
    client.post(url_agregar_producto, data_agregar_producto2, format='json')

    # Obtener el carro creado
    carro = Carro.objects.filter(usuario=user).first()

    # Pagar el carro
    url_pagar_carro = reverse('pagar-carro')
    data_pagar_carro = {'carro_id': carro.id, 'metodo_pago': 'tarjeta'}
    response_pagar_carro = client.post(url_pagar_carro, data_pagar_carro, format='json')

    # Verificar que la venta se creó correctamente
    assert response_pagar_carro.status_code == 200
    assert 'Carro pagado y venta finalizada correctamente.' in response_pagar_carro.data['mensaje']

    # Verificar que los productos se registraron en la venta
    venta = Venta.objects.filter(carro=carro).first()
    assert venta is not None
    assert carro.carroproducto_set.filter(producto=producto1).exists()
    assert carro.carroproducto_set.filter(producto=producto2).exists()


@pytest.mark.django_db
def test_stock_reducido_despues_de_venta():
    # Crear un producto con stock inicial
    producto = Producto.objects.create(
        codigo_producto='PROD100',
        marca='Marca Stock',
        nombre='Producto con Stock',
        precio='20.00',
        stock=10
    )

    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # Agregar el producto al carro
    url_agregar_producto = reverse('agregar-producto-al-carro')
    data_agregar_producto = {'codigo_producto': 'PROD100', 'cantidad': 2}
    client.post(url_agregar_producto, data_agregar_producto, format='json')

    # Obtener el carro creado
    carro = Carro.objects.filter(usuario=user).first()

    # Pagar el carro
    url_pagar_carro = reverse('pagar-carro')
    data_pagar_carro = {'carro_id': carro.id, 'metodo_pago': 'tarjeta'}
    response_pagar_carro = client.post(url_pagar_carro, data_pagar_carro, format='json')

    # Verificar que la venta se creó correctamente
    assert response_pagar_carro.status_code == 200

    # Verificar que el stock del producto se ha reducido correctamente
    producto.refresh_from_db()
    assert producto.stock == 8  # Stock inicial era 10, se restaron 2


@pytest.mark.django_db
def test_detalle_de_venta():
    # Crear un cliente y un producto
    cliente = Cliente.objects.create(
        nombre='Cliente Detalle',
        email='detalle@cliente.com',
        direccion='Calle Detalle 123',
        telefono='987654321'
    )
    producto = Producto.objects.create(
        codigo_producto='DET123',
        marca='Marca Detalle',
        nombre='Producto Detalle',
        precio='40.00',
        stock=5
    )

    # Crear un usuario y autenticar
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.login(username='testuser', password='testpassword')

    # Agregar el producto al carro
    url_agregar_producto = reverse('agregar-producto-al-carro')
    data_agregar_producto = {'codigo_producto': 'DET123', 'cantidad': 1}
    client.post(url_agregar_producto, data_agregar_producto, format='json')

    # Obtener el carro creado
    carro = Carro.objects.filter(usuario=user).first()

    # Pagar el carro
    url_pagar_carro = reverse('pagar-carro')
    data_pagar_carro = {'carro_id': carro.id, 'metodo_pago': 'tarjeta'}
    response_pagar_carro = client.post(url_pagar_carro, data_pagar_carro, format='json')

    # Verificar que la venta se creó correctamente
    assert response_pagar_carro.status_code == 200

    # Obtener los detalles de la venta
    venta = Venta.objects.filter(carro=carro).first()
    url_detalle_venta = reverse('venta-detail', kwargs={'pk': venta.id})
    response_detalle_venta = client.get(url_detalle_venta, {'simple': 'true'}, format='json')  # Solicita 'simple=true'

    # Verificar los detalles de la venta
    assert response_detalle_venta.status_code == 200
    assert response_detalle_venta.data['carro_id'] == carro.id