import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.cliente.models import Cliente, ClienteUsuario
from apps.carro.models import Carro, CarroProducto
from apps.producto.models import Producto
from apps.venta.models import Venta
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def cliente():
    cliente = Cliente.objects.create(nombre="Cliente Test")
    user = User.objects.create(username="clientetest")
    ClienteUsuario.objects.create(cliente=cliente, user=user)
    return cliente

@pytest.fixture
def productos():
    producto1 = Producto.objects.create(nombre="Producto 1")
    producto2 = Producto.objects.create(nombre="Producto 2")
    return [producto1, producto2]

@pytest.mark.django_db
def test_crear_carro_para_cliente_con_productos(api_client, cliente, productos):
    # Obtener el cliente y su usuario asociado
    cliente_usuario = ClienteUsuario.objects.get(cliente=cliente)
    user_id = cliente_usuario.user.id

    # Crear un carro asociado al cliente
    carro_data = {
        'usuario': user_id,
        'productos': [{'producto': p.id, 'cantidad': 1} for p in productos]
    }
    response = api_client.post('/api/carros/', carro_data, format='json')
    assert response.status_code == 201

# Resto de tus pruebas similares ajustadas para usar ClienteUsuario y su relación con User


@pytest.mark.django_db
def test_asociar_venta_a_carro_existente(api_client, cliente, productos):
    # Crear un carro asociado al cliente
    carro = Carro.objects.create(usuario=cliente.usuario)
    for producto in productos:
        CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # Crear una venta asociada al carro
    venta_data = {
        'carro': carro.id,
        'total': sum(p.precio for p in productos),
    }
    response_venta = api_client.post(reverse('venta-list'), venta_data, format='json')
    assert response_venta.status_code == 201

    # Verificar la creación de la venta
    venta_id = response_venta.data['id']
    venta = Venta.objects.get(id=venta_id)
    assert venta.carro == carro
    assert venta.total == sum(p.precio for p in productos)


@pytest.mark.django_db
def test_actualizar_productos_en_carro(api_client, cliente, productos):
    # Crear un carro asociado al cliente con algunos productos
    carro = Carro.objects.create(usuario=cliente.usuario)
    for producto in productos:
        CarroProducto.objects.create(carro=carro, producto=producto, cantidad=1)

    # Crear un nuevo producto y agregarlo al carro
    nuevo_producto = Producto.objects.create(nombre='Producto 3', precio=30.0)
    carro_data = {
        'productos': [{'producto': nuevo_producto.id, 'cantidad': 1}]
    }
    response_carro = api_client.patch(reverse('carro-detail', args=[carro.id]), carro_data, format='json')
    assert response_carro.status_code == 200

    # Verificar la actualización del carro
    carro.refresh_from_db()
    assert carro.carroproducto_set.count() == 3
    assert any(cp.producto == nuevo_producto for cp in carro.carroproducto_set.all())

    # Ahora eliminar uno de los productos originales
    carro_data = {
        'productos': [{'producto': productos[0].id, 'cantidad': 0}]  # Para simular la eliminación
    }
    response_carro = api_client.patch(reverse('carro-detail', args=[carro.id]), carro_data, format='json')
    assert response_carro.status_code == 200

    # Verificar que el producto ha sido eliminado
    carro.refresh_from_db()
    assert carro.carroproducto_set.count() == 2
    assert not any(cp.producto == productos[0] for cp in carro.carroproducto_set.all())


@pytest.mark.django_db
def test_eliminar_carro_y_verificar_integridad_productos(api_client, cliente, productos):
    # Crear un carro asociado al cliente con algunos productos
    carro = Carro.objects.create(usuario=cliente.usuario)
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
