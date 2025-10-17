import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
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
@ensure_csrf_cookie
def catalog_view(request):
    products = Product.objects.all()
    return render(request, 'chatApp/catalog.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'cantidad': 1}
        )
        if not created:
            cart_item.cantidad += 1
            cart_item.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Producto añadido al carrito',
            'cart_count': CartItem.objects.filter(user=request.user).count()
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    items = [{
        'id': item.id,
        'producto': item.product.nombre,
        'cantidad': item.cantidad,
        'subtotal': float(item.subtotal())
    } for item in cart_items]
    
    total = sum(item.subtotal() for item in cart_items)
    
    return JsonResponse({
        'items': items,
        'total': float(total)
    })

# --- Vista de descarga ---
def download_view(request):
    return render(request, 'chatApp/download.html')

# --- Autenticación ---
@require_http_methods(["POST"])
def login_api(request):
    # Parse JSON
    if not request.body:
        return JsonResponse({'status': 'error', 'message': 'No se recibieron datos'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Formato de datos inválido'}, status=400)

    username = data.get('username')
    email = data.get('email')
    password = data.get('password', '')

    if not password or (not username and not email):
        return JsonResponse({'status': 'error', 'message': 'Faltan credenciales'}, status=400)

    user = None

    # Try authenticate by username first (if provided)
    if username:
        user = authenticate(request, username=username, password=password)

    # If not authenticated by username, try by email lookup
    if user is None and email:
        try:
            uobj = User.objects.get(email=email)
            user = authenticate(request, username=uobj.username, password=password)
        except User.DoesNotExist:
            # keep user as None
            pass

    # If still no user, respond with 401 (unauthorized)
    if user is None:
        return JsonResponse({'success': False, 'error': 'Credenciales incorrectas o usuario no existe'}, status=401)

    if not user.is_active:
        return JsonResponse({'success': False, 'error': 'Cuenta desactivada'}, status=401)

    # Login the user
    login(request, user)
    return JsonResponse({'success': True, 'message': 'Inicio de sesión exitoso'})

@require_http_methods(["POST"])
def register_api(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validar que no exista el usuario o email
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'El nombre de usuario ya está en uso'
            }, status=400)
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'El email ya está registrado'
            }, status=400)
            
        # Crear nuevo usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Iniciar sesión automáticamente
        login(request, user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Usuario registrado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Error en el formato de los datos'
        }, status=400)

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


# --- Logout ---
@require_http_methods(["POST"])
def logout_api(request):
    logout(request)
    return JsonResponse({
        'status': 'success',
        'message': 'Sesión cerrada exitosamente'
    })

# --- Carrito ---
