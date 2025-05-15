import datetime
from django.db import models

# Create your models here.
class Categoria(models.Model):
    idCategoria = models.IntegerField(primary_key=True, verbose_name='Id Categoria') 
    nombreCategoria= models.CharField(max_length=40, verbose_name='Nombre Categoria')

    def __str__(self):
        return self.nombreCategoria
    
class Producto(models.Model):
    idProducto = models.CharField(primary_key=True, max_length=5, verbose_name='Id Producto')
    nombre = models.CharField(max_length=50, verbose_name='Nombre del producto')
    descripcion = models.CharField(max_length=400,verbose_name='Descripcion de producto')
    precio = models.IntegerField(null=True, verbose_name='Ingrese precio producto')
    imagen= models.ImageField(upload_to="imagenes", null=True, verbose_name='Imagen')
    categoria= models.ForeignKey('Categoria', on_delete=models.CASCADE, verbose_name='Categoria')

    def __str__(self):
        return self.idProducto

opciones_consultas= [
    [0, "Consulta"],
    [1, "Reclamo"],
    [2, "Sugerencia"],
    [3, "Felicitaciones"],
    [4, "Despacho"],
    [5, "Devolución"],
    [6, "Objeto dañado"]
]
class Contacto(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    correo = models.EmailField(max_length=50, verbose_name='Correo electrónico')
    tipo_consulta = models.IntegerField(choices=opciones_consultas)
    mensaje = models.TextField()
    avisos = models.BooleanField()

    def __str__(self):
        return self.nombre
    
class Boleta(models.Model):
    id_boleta=models.AutoField(primary_key=True)
    total=models.BigIntegerField()
    fechaCompra=models.DateTimeField(blank=False, null=False, default = datetime.datetime.now)
  
    def __str__(self):
        return str(self.id_boleta)

class detalle_boleta(models.Model):
    id_boleta = models.ForeignKey('Boleta', blank=True, on_delete=models.CASCADE)
    id_detalle_boleta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.BigIntegerField()

    def __str__(self):
        return str(self.id_detalle_boleta)
