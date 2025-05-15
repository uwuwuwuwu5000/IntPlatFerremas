from django.contrib import admin
from .models import Categoria, Producto, Contacto, Boleta, detalle_boleta
from .forms import ProductoForm

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria','stock']
    list_editable = ['precio']
    search_fields = ['nombre']
    list_filter = ['categoria']
    list_per_page = 6
    form = ProductoForm

class BoletaAdmin(admin.ModelAdmin):
    list_display = ('id_boleta','total','fechaCompra')

class DetalleBoletaAdmin(admin.ModelAdmin):
    list_display = ('id_boleta','id_detalle_boleta','id_producto','cantidad','subtotal')

admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Contacto)
admin.site.register(Boleta,BoletaAdmin)
admin.site.register(detalle_boleta,DetalleBoletaAdmin)