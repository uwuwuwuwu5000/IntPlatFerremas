from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from .models import Boleta, Producto, Categoria, detalle_boleta, Pedido, DetallePedido
from ferreteria.carrito import Carrito
from .forms import ContactoForm, CustomUserProfileForm, ProductoForm, CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from rest_framework import viewsets
from .serializers import ProductoSerializer
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
import bcchapi
from datetime import datetime,timedelta
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import io
from docx.shared import Inches


# Create your views here.

class CategoriaViewset(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = ProductoSerializer

class ProductoViewset(viewsets.ModelViewSet): #Componente que se encarga de guardar los datos
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_queryset(self):
        productos = Producto.objects.all()
                         #DICCIONARIO.metodo
        nombre = self.request.GET.get('nombre')

        if nombre:
            productos = productos.filter(nombre__constains=nombre)

        return productos

class UserCreateView(CreateView):
    model = User
    form_class = CustomUserProfileForm
    template_name = 'registration/perfil.html'

#Banco central
def obtener_valor_dolar():
    user = "es.ibarra@duocuc.cl"
    password = "Uwu7832!"
    siete = bcchapi.Siete(user, password)
    today = datetime.now()
    today = today.strftime("%Y-%m-%d")
    cuadro = siete.cuadro(
        series=["F073.TCO.PRE.Z.D"],
        nombres = ["dolar"],
        desde = today,
        hasta = today,
        observado = {"dolar":"last"}
    )

    if not cuadro.empty:
        valor_dolar = cuadro.iloc[0]["dolar"]
    else:
        valor_dolar = "No disponible"

    return valor_dolar

def perfil(request):
    return render(request, 'registration/perfil.html')

def index(request):
    return render(request, 'index.html')

def productos(request):
    producto = Producto.objects.all() 
    data = {
        'productos': producto
    }
    return render(request, 'productos.html', data)

def nosotros(request):
    data = {
        'form': ContactoForm()
    }

    if request.method == 'POST':
        formulario = ContactoForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            data["mensaje"] = "Contacto guardado"
        else:
            data["form"] = formulario
    return render (request, 'nosotros.html', data )

@login_required
def cerrar(request):
    logout(request)
    return redirect('index')

def registrar(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request, "Te has registrado correctamente")
            return redirect(to="index")
        data['form'] = formulario  
        
    return render(request, 'registration/registrar.html',data)

@permission_required ('ferreteria.add_producto')      
def agregar(request):

    data = {
        'form': ProductoForm()
    }

    if request.method== 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto agregado")
        else:
            data["form"] = formulario
    return render(request, 'producto/agregar.html', data)

@permission_required ('ferreteria.view_producto')
def lista(request):
    productos = Producto.objects.all()
    data={
       'producto': productos
    }
    
    return render(request, 'producto/lista.html', data)

@permission_required ('ferreteria.change_producto')
def modificar(request, id):

    producto = get_object_or_404(Producto, idProducto=id)

    data = {
        'form': ProductoForm(instance=producto)
    }

    if request.method== 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado correctamente")
        return redirect(to="lista")
    
    return render (request, 'producto/modificar.html', data)

@login_required
def detalle_producto(request, id):
    producto = get_object_or_404(Producto, idProducto=id)   
    return render (request, 'detalleProducto.html', {'producto':producto})

@permission_required ('ferreteria.delete_producto')
def eliminar(request, id):
    producto = get_object_or_404(Producto, idProducto=id)
    producto.delete()
    messages.success(request, "Eliminado correctamente")
    return redirect(to="lista")

#Tienda y funcion banco Central
@login_required
def tienda(request):
    productos = Producto.objects.all()
    valor_dolar = obtener_valor_dolar()
    return render(request, 'tienda.html', {
        'productos': productos,
        "valor_dolar":valor_dolar
        })
    
#Carrito
def agregar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(idProducto=id)
    if producto.stock > 0:
        carrito.agregar(producto)
        messages.success(request, "Producto añadido al carrito.")
    else:
        messages.error(request, "No hay suficiente stock.")
    return redirect('tienda')

def eliminar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(idProducto=id)
    carrito.eliminar(producto)
    return redirect('tienda')

def restar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(idProducto=id)
    carrito.restar(producto)
    return redirect('tienda')

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar() 
    return redirect('tienda')

#boleta
def generarBoleta(request):
    precio_total=0
    productos = []

    #Calculo de precio
    for key, value in request.session['carrito'].items():
        precio_total = precio_total + int(value['precio']) * int(value['cantidad'])
    boleta = Boleta(total = precio_total)
    boleta.save()

    #Validar stock 
    for key, value in request.session['carrito'].items():
        producto = Producto.objects.get(idProducto=value['producto_id'])
        if producto.stock < value['cantidad']:
            messages.error(request, f"No hay suficiente stock para {producto.nombre}.")
            return redirect('tienda')

    #Detalle boleta
    for key, value in request.session['carrito'].items():
            producto = Producto.objects.get(idProducto = value['producto_id'])
            cant = value['cantidad']
            subtotal = cant * int(value['precio'])
            detalle = detalle_boleta(id_boleta = boleta, id_producto = producto, cantidad = cant, subtotal = subtotal)
            detalle.save()
            producto.stock -= cant
            producto.save()
            productos.append(detalle)
    datos={
        'productos':productos,
        'fecha':boleta.fechaCompra,
        'total': boleta.total
    }
    request.session['boleta'] = boleta.id_boleta
    carrito = Carrito(request)
    carrito.limpiar()
    return render(request, 'detallecarrito.html',datos)

#Correo
def enviar_correo(request):
    if request.method == 'POST':
        send_mail(
            subject='Asunto del correo',
            message='Este es el cuerpo del correo',
            from_email='pruebaskk1221@gmail.com',
            recipient_list=['kkroto1221@correo.com'],
            fail_silently=False,
        )
        return HttpResponseRedirect(reverse('correo_enviado')) 
    return render(request, 'enviar.html')

#Pedido
from rest_framework.views import APIView
from rest_framework.response import Response
from transbank.webpay.webpay_plus.transaction import Transaction
import logging
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from random import randint

transaction = Transaction(
    WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    )
)

def generarPedido(request):
    precio_total=0
    productos = []
    carrito = request.session.get('carrito', {})

    #Validar carrito vacio
    if not carrito:
        messages.error(request, "No puedes realizar una compra con el carrito vacío.")
        return redirect('tienda') 

    tipo_envio = request.POST.get('tipo_envio')
    medio_pago = request.POST.get('medio_pago')

    #Calculo de precio
    for key, value in request.session['carrito'].items():
        precio_total += int(value['precio']) * int(value['cantidad'])

    if tipo_envio == 'domicilio':
        precio_total += 5000

    #Crear un pedido
    pedido_obj = Pedido.objects.create(
        user = request.user,
        estado = 'creado',
        tipo_envio=tipo_envio,
        tipo_pago=medio_pago,
        total = precio_total
    )

    #Validar stock 
    for key, value in request.session['carrito'].items():
        producto = Producto.objects.get(idProducto=value['producto_id'])
        if producto.stock < value['cantidad']:
            messages.error(request, f"No hay suficiente stock para {producto.nombre}.")
            return redirect('tienda')

    #Detalle pedido
    for key, value in request.session['carrito'].items():
            producto = Producto.objects.get(idProducto = value['producto_id'])
            cant = value['cantidad']
            subtotal = cant * int(value['precio'])
            detalle = DetallePedido.objects.create(
                 id_pedido=pedido_obj,
                 id_producto = producto,
                 cantidad=cant,
                 subtotal=subtotal
            )
            producto.stock -= cant
            producto.save()
            productos.append(detalle)
    datos={
        'productos':productos,
        'fecha':pedido_obj.fecha_compra,
        'tipo_envio':pedido_obj.tipo_envio,
        'total': pedido_obj.total
    }

    request.session['id_pedido'] = pedido_obj.id_pedido
    carrito = Carrito(request)
    carrito.limpiar()
    response = transaction.create(
                buy_order=str(pedido_obj.id_pedido),
                session_id=str(randint(100000, 999999)),
                amount=str(pedido_obj.total),
                return_url='http://localhost:8000/webpay/respuesta/'
            )
    return render(request, 'webpay_redirigir.html', {
            'url': response['url'],
            'token': response['token']
        })

def webpay_respuesta(request):
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    result = transaction.commit(token)
    return render(request, 'webpay_respuesta.html', {'resultado': result})

@permission_required ('ferreteria.view_producto')
def orden_pedidos(request):
    pedidos = Pedido.objects.all()
    data = {}
    
    data = {'pedido':pedidos}
    return render(request, 'bodega.html', data)

@permission_required ('ferreteria.view_producto')
def detalle_pedidos(request,id):
    detalles = DetallePedido.objects.filter(id_pedido=id)
    return render (request, 'bodegaPedido.html', {'detalles':detalles})

def despachar(request, id):
    if request.method == "POST":
        pedido = get_object_or_404(Pedido,id_pedido = id)
        pedido.estado = "despachado"
        pedido.save()

    return redirect('bodega')

def admin_view(request):
    pedidos = Pedido.objects.all()
    data = {}
    
    data = {'pedido':pedidos}
    return render(request, 'administrador.html', data)

def detalle_pedidosAdmin(request,id):
    detalles = DetallePedido.objects.filter(id_pedido=id)
    return render (request, 'detallepedido.html', {'detalles':detalles})

def exportar_reporte_mensual(request):
    mes_actual =datetime.now().month
    año_actual = datetime.now().year
    #Cambiar a pagadooo!!!!!!
    estado = "despachado"
    
    pedidosVendidos = Pedido.objects.filter(
        fecha_compra__year=año_actual,
        fecha_compra__month=mes_actual,
        estado = estado
    )

    # Convertir queryset a DataFrame
    df = pd.DataFrame.from_records(
        pedidosVendidos.values('id_pedido', 'fecha_compra', 'user__username', 'estado', 'tipo_envio', 'total')
    )

    total_pedidos = df.shape[0]
    total_vendido = df['total'].sum()
    pedidos_entregados = df[df['estado'] == 'entregado'].shape[0]

    # Crear el documento Word
    doc = Document()
    doc.add_heading('Informe de Ventas - Mes Actual', 0)

    doc.add_paragraph(f'Mes: {mes_actual} / Año: {año_actual}')
    doc.add_paragraph(f'Total de pedidos realizados: {total_pedidos}')
    doc.add_paragraph(f'Total de pedidos entregados: {pedidos_entregados}')
    doc.add_paragraph(f'Total vendido: ${total_vendido:,}')

    # Agregar tabla de pedidos
    doc.add_heading('Detalle de pedidos', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Light Grid'

    # Encabezados
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col.replace('_', ' ').capitalize()

    # Filas
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)

    # Responder con archivo Word
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename=Informe_VentasFerremas_{mes_actual}_{año_actual}.docx'
    doc.save(response)
    return response