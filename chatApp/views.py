import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Message, Product, CartItem


# --- Vista principal ---
def chat_view(request):
    avatars = [
        static('images/avatars/avatar1.png'),
        static('images/avatars/avatar2.png'),
        static('images/avatars/avatar3.png'),
    ]
    # Cargar productos ficticios si no existen
    if Product.objects.count() == 0:
        Product.objects.bulk_create([
            Product(nombre="Mouse Gamer RGB", precio=19990),
            Product(nombre="Teclado Mecánico", precio=29990),
            Product(nombre="Headset 7.1", precio=24990),
            Product(nombre="Monitor 144Hz", precio=139990),
            Product(nombre="Silla Ergonómica", precio=89990),
            Product(nombre="Pad XXL", precio=9990),
        ])

    products = Product.objects.all()
    return render(request, 'chatApp/index.html', {'avatars': avatars, 'products': products})

# --- Vista del catálogo ---
def catalog_view(request):
    return render(request, 'chatApp/catalog.html')

# --- Vista de descarga ---
def download_view(request):
    return render(request, 'chatApp/download.html')

# --- API de mensajes ---
@require_http_methods(["GET", "POST"])
def messages_api(request):
    if request.method == 'GET':
        tab = request.GET.get('tab', 'nacional')
        msgs = Message.objects.filter(tab=tab).order_by('timestamp')
        data = [{
            'id': m.id,
            'text': m.text,
            'avatar': m.avatar,
            'timestamp': m.timestamp.strftime('%d/%m/%Y %H:%M'),
            'sender': m.sender or ''
        } for m in msgs]
        return JsonResponse({'messages': data})

    # POST → guardar mensaje
    try:
        payload = json.loads(request.body.decode('utf-8'))
        text = payload.get('text', '').strip()
        tab = payload.get('tab', 'nacional')
        avatar = payload.get('avatar', '')
        sender = payload.get('sender', '')
        if not text:
            return HttpResponseBadRequest('Mensaje vacío')
        m = Message.objects.create(text=text, tab=tab, avatar=avatar, sender=sender)
        return JsonResponse({'message': {
            'id': m.id,
            'text': m.text,
            'avatar': m.avatar,
            'timestamp': m.timestamp.strftime('%d/%m/%Y %H:%M'),
            'sender': m.sender or ''
        }})
    except Exception as e:
        return HttpResponseBadRequest(str(e))


# --- Registro/Login/Logout ---
@csrf_exempt
def register_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "El usuario ya existe"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "El correo electrónico ya está registrado"}, status=400)

        User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({"success": True, "message": "Usuario registrado correctamente"})
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def login_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        user = authenticate(request, username=username, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "Credenciales incorrectas"}, status=401)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def logout_api(request):
    logout(request)
    return JsonResponse({"success": True})


# --- Carrito ---
@login_required
def get_cart(request):
    # Only allow GET for retrieving cart
    if request.method != 'GET':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    items = CartItem.objects.filter(user=request.user)
    data = [{
        "nombre": i.product.nombre,
        "precio": float(i.product.precio),
        "cantidad": i.cantidad,
        "subtotal": float(i.subtotal())
    } for i in items]
    return JsonResponse({"items": data})


@login_required
def add_to_cart(request):
    # Only POST allowed
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data = json.loads(request.body)
        pid = data.get("product_id")
        cantidad = int(data.get("cantidad", 1))

        prod = Product.objects.get(id=pid)
        item, created = CartItem.objects.get_or_create(user=request.user, product=prod)

        if not created:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()

        return JsonResponse({"success": True})
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    except ValueError:
        return JsonResponse({"error": "Cantidad inválida"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
