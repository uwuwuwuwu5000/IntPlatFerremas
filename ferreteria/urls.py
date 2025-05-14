from django.urls import path, include
from . import views
from .views import ProductoViewset, CategoriaViewset
from rest_framework import routers

#Permite crear las url necesarias para nuestra app
router = routers.DefaultRouter()
router.register('producto', ProductoViewset) #Urls que genera router
router.register('categoria', CategoriaViewset)

urlpatterns=[
    path('', views.index, name="index"),
    path('perfil/', views.perfil, name="perfil"),
    path('logout/', views.cerrar, name="cerrar"),
    path('registrar/', views.registrar, name="registrar"),

    path('tienda/', views.tienda, name="tienda"),
    path('agregar/<id>', views.agregar_producto, name="add"),
    path('eliminar/<id>', views.eliminar_producto, name="del"),
    path('restar/<id>', views.restar_producto, name="sub"),
    path('limpiar/', views.limpiar_carrito, name="cls"),
    path('generarBoleta/', views.generarBoleta,name="generarBoleta"),

    path('nosotros/', views.nosotros, name="nosotros"),
    path('productos/', views.productos, name="productos"),
    path('detalle/<id>/', views.detalle_producto, name="detalle"),
    path('agregar/', views.agregar, name="agregar"),
    path('modificar/<id>/', views.modificar, name="modificar"),
    path('lista/', views.lista, name="lista"),
    path('eliminar/<id>/', views.eliminar, name="eliminar"),  
    path('api/', include(router.urls)),
]