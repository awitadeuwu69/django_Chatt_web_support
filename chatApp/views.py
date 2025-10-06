import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from .models import Message
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem

def chat_view(request):
    # Avatares predefinidos en static/chatApp/avatars/
    avatars = [
        static('images/avatars/avatar1.png'),
        static('images/avatars/avatar2.png'),
        static('images/avatars/avatar3.png'),
    ]
    return render(request, 'chatApp/index.html', {'avatars': avatars})

@require_http_methods(["GET", "POST"])
def messages_api(request):
    if request.method == 'GET':
        tab = request.GET.get('tab', 'nacional')
        msgs = Message.objects.filter(tab=tab).order_by('timestamp')
        data = [{
            'id': m.id,
            'text': m.text,
            'avatar': m.avatar,
            'timestamp': m.timestamp.strftime('%d/%m/%Y %H:%M')
        } for m in msgs]
        return JsonResponse({'messages': data})

    # POST → guardar mensaje
    try:
        payload = json.loads(request.body.decode('utf-8'))
        text = payload.get('text', '').strip()
        tab = payload.get('tab', 'nacional')
        avatar = payload.get('avatar', '')
        if not text:
            return HttpResponseBadRequest('Mensaje vacío')
        m = Message.objects.create(text=text, tab=tab, avatar=avatar)
        return JsonResponse({'message': {
            'id': m.id,
            'text': m.text,
            'avatar': m.avatar,
            'timestamp': m.timestamp.strftime('%d/%m/%Y %H:%M')
        }})
    except Exception as e:
        return HttpResponseBadRequest(str(e))
@csrf_exempt
def register_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "El usuario ya existe"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        return JsonResponse({"success": True, "message": "Usuario registrado correctamente"})
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def login_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
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
@csrf_exempt
@login_required
def get_cart(request):
    items = CartItem.objects.filter(user=request.user)
    data = [{
        "nombre": i.product.nombre,
        "precio": float(i.product.precio),
        "cantidad": i.cantidad,
        "subtotal": float(i.subtotal())
    } for i in items]
    return JsonResponse({"items": data})

@csrf_exempt
@login_required
def add_to_cart(request):
    data = json.loads(request.body)
    pid = data.get("product_id")
    cantidad = data.get("cantidad", 1)

    try:
        prod = Product.objects.get(id=pid)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

    item, created = CartItem.objects.get_or_create(user=request.user, product=prod)
    if not created:
        item.cantidad += cantidad
    else:
        item.cantidad = cantidad
    item.save()

    return JsonResponse({"success": True})


