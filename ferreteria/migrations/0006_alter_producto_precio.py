# Generated by Django 5.0.6 on 2024-06-21 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferreteria', '0005_alter_producto_precio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='precio',
            field=models.IntegerField(null=True, verbose_name='Ingrese precio producto'),
        ),
    ]
