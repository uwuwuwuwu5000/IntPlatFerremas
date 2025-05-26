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
    path('generarPedido/', views.generarPedido,name="generarPedido"),

    path('nosotros/', views.nosotros, name="nosotros"),
  
    path('detalle/<id>/', views.detalle_producto, name="detalle"),
    path('agregar/', views.agregar, name="agregar"),
    path('modificar/<id>/', views.modificar, name="modificar"),
    path('lista/', views.lista, name="lista"),
    # Bodega
    path('bodega/', views.orden_pedidos, name="bodega"),
    path('bodegaPedido/<id>', views.detalle_pedidos, name="bodegaPedido"),
    path('despachar/<id>',views.despachar, name="despachar"),

    #Administrador
    path('administrador/', views.admin_view, name="administrador"),
    path('detallepedido/<id>', views.detalle_pedidosAdmin, name="detallepedido"),
    path('exportar-informe/', views.exportar_reporte_mensual, name='exportar_informe'),


    path('eliminar/<id>/', views.eliminar, name="eliminar"),  
    path('api/', include(router.urls)),
    path('webpay/iniciar/', views.generarPedido, name='webpay_iniciar'),
    path('webpay/respuesta/', views.webpay_respuesta, name='webpay_respuesta'),
]