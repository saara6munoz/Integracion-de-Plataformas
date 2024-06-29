# Generated by Django 5.0.6 on 2024-06-29 04:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('venta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pago', models.DateTimeField(auto_now_add=True)),
                ('cantidad_pagada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metodo_pago', models.CharField(choices=[('Tarjeta', 'Tarjeta'), ('Efectivo', 'Efectivo'), ('Transferencia', 'Transferencia')], max_length=50)),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venta.venta')),
            ],
        ),
    ]
