from django.contrib import admin
from .models import Categoria, Producto, Contacto
from .forms import ProductoForm

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria']
    list_editable = ['precio']
    search_fields = ['nombre']
    list_filter = ['categoria']
    list_per_page = 6
    form = ProductoForm


admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Contacto)