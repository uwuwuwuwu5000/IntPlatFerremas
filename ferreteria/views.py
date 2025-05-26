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
    return render(request, 'detallepedido.html',datos)

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

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
import random

# Configuración global de Webpay (debería ir al inicio del archivo)
webpay_transaction = Transaction(
    WebpayOptions(
        commerce_code='597055555532', 
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    )
)

def generarPedido(request):
    # Validar carrito vacío primero
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "No puedes realizar una compra con el carrito vacío.")
        return redirect('tienda')

    if request.method == 'POST':
        tipo_envio = request.POST.get('tipo_envio')
        medio_pago = request.POST.get('medio_pago')

        # Calcular precio total
        precio_total = sum(int(item['precio']) * int(item['cantidad']) for item in carrito.values())
        
        if tipo_envio == 'domicilio':
            precio_total += 5000

        # Validar stock
        for key, value in carrito.items():
            producto = Producto.objects.get(idProducto=value['producto_id'])
            if producto.stock < value['cantidad']:
                messages.error(request, f"No hay suficiente stock para {producto.nombre}.")
                return redirect('tienda')

        # Crear pedido (en estado pendiente para Webpay)
        pedido_obj = Pedido.objects.create(
            user=request.user,
            estado='pendiente',
            tipo_envio=tipo_envio,
            tipo_pago=medio_pago,
            total=precio_total
        )

        # Si el medio de pago es Webpay
        if medio_pago == 'webpay':
            try:
                buy_order = str(pedido_obj.id_pedido)
                session_id = str(random.randint(100000, 999999))
                return_url = f'http://{request.get_host()}/webpay/respuesta/'
                
                response = webpay_transaction.create(
                    buy_order=buy_order,
                    session_id=session_id,
                    amount=precio_total,
                    return_url=return_url
                )
                
                # Guardar datos importantes en sesión
                request.session['webpay_token'] = response['token']
                request.session['webpay_order'] = buy_order
                request.session['id_pedido'] = pedido_obj.id_pedido
                
                # Redirigir a Webpay
                return render(request, 'webpay_redirigir.html', {
                    'url': response['url'],
                    'token': response['token']
                })
            except Exception as e:
                messages.error(request, f"Error al conectar con Webpay: {str(e)}")
                return redirect('carrito')
        
        # Para otros métodos de pago
        else:
            return procesar_pedido_completo(request, pedido_obj, carrito)

    return redirect('carrito')

from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from django.template.loader import render_to_string

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def generar_pdf_pedido(pedido, detalles):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Obtener estilos base y modificar solo lo necesario
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados solo si no existen
    if 'CustomTitle' not in styles:
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
    
    if 'CustomSubtitle' not in styles:
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
    
    elements = []
    
    # Título usando el estilo personalizado
    elements.append(Paragraph("FERRETERIA FERREMAS", styles['CustomTitle']))
    elements.append(Paragraph("COMPROBANTE DE PEDIDO", styles['CustomSubtitle']))
    elements.append(Spacer(1, 20))
    
    # Resto del código permanece igual...
    pedido_info = [
        ["N° Pedido:", str(pedido.id_pedido)],
        ["Fecha:", pedido.fecha_compra.strftime("%d/%m/%Y %H:%M")],
        ["Cliente:", pedido.user.username],
        ["Estado:", pedido.estado.capitalize()],
        ["Tipo de envío:", pedido.tipo_envio.capitalize()],
        ["Total:", f"${pedido.total:,}"],
    ]
    
    pedido_table = Table(pedido_info, colWidths=[100, 200])
    pedido_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(pedido_table)
    elements.append(Spacer(1, 30))
    
    # Detalles del pedido
    elements.append(Paragraph("Detalles del Pedido", styles['Heading2']))
    
    detalle_data = [["Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
    for detalle in detalles:
        detalle_data.append([
            detalle.id_producto.nombre,
            str(detalle.cantidad),
            f"${int(detalle.subtotal/detalle.cantidad):,}",
            f"${detalle.subtotal:,}"
        ])
    
    detalle_table = Table(detalle_data, colWidths=[200, 80, 100, 100])
    detalle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(detalle_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def enviar_pedido_por_correo(pedido, detalles, destinatario):
    # Generar PDF
    pdf = generar_pdf_pedido(pedido, detalles)
    
    # Crear mensaje de correo
    subject = f'Confirmación de Pedido #{pedido.id_pedido} - Ferreteria Ferremas'
    body = render_to_string('email_pedido.html', {
        'pedido': pedido,
        'detalles': detalles,
    })
    
    email = EmailMessage(
        subject,
        body,
        'pruebaskk1221@gmail.com',  # Remitente
        ['kkroto1221@gmail.com'],             # Destinatario
    )
    email.content_subtype = "html"  # Para contenido HTML
    
    # Adjuntar PDF
    email.attach(
        f'pedido_{pedido.id_pedido}.pdf',
        pdf,
        'application/pdf'
    )
    
    email.send()

def procesar_pedido_completo(request, pedido_obj, carrito):
    # Crear detalles del pedido
    productos = []
    for key, value in carrito.items():
        producto = Producto.objects.get(idProducto=value['producto_id'])
        cant = value['cantidad']
        subtotal = cant * int(value['precio'])
        
        DetallePedido.objects.create(
            id_pedido=pedido_obj,
            id_producto=producto,
            cantidad=cant,
            subtotal=subtotal
        )
        
        producto.stock -= cant
        producto.save()
        productos.append(producto)
    
    # Actualizar estado del pedido
    pedido_obj.estado = 'completado'
    pedido_obj.save()
    
    # Obtener detalles para el PDF y correo
    detalles = DetallePedido.objects.filter(id_pedido=pedido_obj)
    
    # Enviar correo con PDF adjunto
    try:
        enviar_pedido_por_correo(pedido_obj, detalles, request.user.email)
        messages.success(request, "Se ha enviado un correo con los detalles de tu pedido.")
    except Exception as e:
        messages.warning(request, f"Pedido completado, pero hubo un error al enviar el correo: {str(e)}")
    
    # Limpiar carrito
    carrito = Carrito(request)
    carrito.limpiar()
    
    # Mostrar confirmación
    return render(request, 'detallepedido.html', {
        'detalles': detalles,
        'fecha': pedido_obj.fecha_compra,
        'total': pedido_obj.total,
        'tipo_envio': pedido_obj.tipo_envio
    })

def webpay_respuesta(request):
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    
    if not token:
        messages.error(request, "Token de Webpay no recibido")
        return redirect('carrito')
    
    try:
        # Confirmar transacción con Webpay
        response = webpay_transaction.commit(token)
        
        if response.get('status') == 'AUTHORIZED':
            # Pago exitoso
            pedido_id = request.session.get('id_pedido')
            pedido = Pedido.objects.get(id_pedido=pedido_id)
            
            # Verificar que el pedido no haya sido procesado antes
            if pedido.estado == 'pendiente':
                carrito = request.session.get('carrito', {})
                return procesar_pedido_completo(request, pedido, carrito)
            else:
                messages.success(request, "Pedido ya fue procesado anteriormente")
                return redirect('detallepedido')
        else:
            # Pago fallido
            messages.error(request, "El pago no pudo ser procesado. Por favor intenta nuevamente.")
            return redirect('productos')
            
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {str(e)}")
        return redirect('tienda')

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