# Generated by Django 5.0.6 on 2024-06-26 20:19

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferreteria', '0009_alter_contacto_tipo_consulta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boleta',
            fields=[
                ('id_boleta', models.AutoField(primary_key=True, serialize=False)),
                ('total', models.BigIntegerField()),
                ('fechaCompra', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='detalle_boleta',
            fields=[
                ('id_detalle_boleta', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('subtotal', models.BigIntegerField()),
                ('id_boleta', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='ferreteria.boleta')),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ferreteria.producto')),
            ],
        ),
    ]
