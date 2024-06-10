import pytest
from apps.productos.models import Producto

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
