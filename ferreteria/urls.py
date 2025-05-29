from django.urls import path, include
from . import views
from . import views_kk
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

    path('tienda/', views_kk.tienda, name="tienda"),
    path('agregar/<id>', views_kk.agregar_producto, name="add"),
    path('eliminar/<id>', views_kk.eliminar_producto, name="del"),
    path('restar/<id>', views_kk.restar_producto, name="sub"),
    path('limpiar/', views_kk.limpiar_carrito, name="cls"),
    path('generarBoleta/', views_kk.generarBoleta,name="generarBoleta"),
    path('generarPedido/', views_kk.generarPedido,name="generarPedido"),

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
    path('webpay/iniciar/', views_kk.generarPedido, name='webpay_iniciar'),
    path('webpay/respuesta/', views_kk.webpay_respuesta, name='webpay_respuesta'),
]