# Agregar estos imports al inicio de tu views.py
import json
import os
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.models import LogEntry  # <-- 1. LÍNEA AÑADIDA
from .models import Message, Product, CartItem, UserProfile


from .youtube_service import get_youtube_events
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test


def admin_required(function):
    """
    Decorator for views that require the user to be an administrator.
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return function(request, *args, **kwargs)
        else:
            # Redirect to the home page or show a 403 Forbidden error.
            # messages.error(request, "You do not have permission to access this page.")
            return redirect('chatApp:index') # Assuming 'index' is the name of your main view.
    
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

import datetime
import requests
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone

# Cache para la IP pública
public_ip_cache = None

@login_required
@admin_required
def admin_dashboard(request):
    """
    Muestra el panel de administración con perfiles de usuario, búsqueda,
    ordenamiento y un panel maestro con estadísticas del sistema.
    """
    global public_ip_cache
    # --- Lógica del Panel Maestro ---

    # 1. Tiempo de actividad del servidor
    uptime_delta = datetime.datetime.now() - settings.SERVER_START_TIME
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    # 2. Usuarios conectados (sesiones activas)
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()

    # 3. IP pública (con caché simple)
    if public_ip_cache is None:
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            response.raise_for_status()
            public_ip_cache = response.json().get('ip', 'No disponible')
        except requests.RequestException:
            public_ip_cache = 'No se pudo obtener'
    
    public_ip = public_ip_cache

    # --- Lógica de la tabla de usuarios ---
    user_profiles = UserProfile.objects.select_related('user')

    # Parámetros de búsqueda y ordenamiento
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'date_desc')

    # Búsqueda por nombre de usuario
    if search_query:
        user_profiles = user_profiles.filter(user__username__icontains=search_query)

    # Lógica de ordenamiento
    order_field = '-user__date_joined' # Default
    if sort_by == 'date_asc':
        order_field = 'user__date_joined'
    elif sort_by == 'date_desc':
        order_field = '-user__date_joined'
    elif sort_by == 'role_asc':
        order_field = 'role'
    elif sort_by == 'role_desc':
        order_field = '-role'
    
    user_profiles = user_profiles.order_by(order_field)

    context = {
        'user_profiles': user_profiles,
        'search_query': search_query,
        'sort_by': sort_by,
        'master_panel': {
            'uptime': uptime_str,
            'active_sessions': active_sessions,
            'public_ip': public_ip,
        }
    }

    return render(request, 'chatApp/admin_dashboard.html', context)


@login_required
@admin_required
def user_profile_detail_view(request, username):
    """
    Muestra los detalles del perfil de un usuario específico.
    """
    try:
        user_obj = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user_obj)
        return render(request, 'chatApp/user_profile_detail.html', {
            'profile': profile,
            'user': user_obj
        })
    except User.DoesNotExist:
        messages.error(request, f"El usuario '{username}' no existe.")
        return redirect('chatApp:admin_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, f"El perfil para el usuario '{username}' no fue encontrado.")
        return redirect('chatApp:admin_dashboard')



def update_events_api(request):
    youtube_events = get_youtube_events()
    # Añadir origin dinámico si no está presente (ayuda con restricciones de embed)
    origin = f"{request.scheme}://{request.get_host()}"
    for ev in youtube_events:
        if ev.get('embed_url') and 'origin=' not in ev['embed_url']:
            sep = '&' if '?' in ev['embed_url'] else '&'
            ev['embed_url'] = ev['embed_url'] + f'&origin={origin}'
    return JsonResponse(youtube_events, safe=False)


# --- Vista de perfil ---
def index_view(request):
    youtube_events = get_youtube_events()
    # Forzar origin en los embed_url para que YouTube acepte el iframe desde este dominio
    origin = f"{request.scheme}://{request.get_host()}"
    for ev in youtube_events:
        if ev.get('embed_url') and 'origin=' not in ev['embed_url']:
            ev['embed_url'] = ev['embed_url'] + f'&origin={origin}'

    return render(request, 'chatApp/index.html', {'youtube_events': youtube_events})

@login_required
def profile_view(request):
    """Vista principal del perfil del usuario"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'chatApp/profile.html', {
        'profile': profile
    })


# --- Actualizar perfil ---
@login_required
@csrf_exempt
def update_profile_api(request):
    """API para actualizar información del perfil"""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Actualizar username del usuario
        new_username = data.get('username')
        if new_username and new_username != request.user.username:
            # Verificar si el username ya existe
            if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                return JsonResponse({
                    "success": False,
                    "error": "Este nombre de usuario ya está en uso"
                }, status=400)
            request.user.username = new_username
            request.user.save()

        # Actualizar email del usuario
        new_email = data.get('email')
        if new_email and new_email != request.user.email:
            # Verificar si el email ya existe
            if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                return JsonResponse({
                    "success": False,
                    "error": "Este correo electrónico ya está en uso"
                }, status=400)
            request.user.email = new_email
            request.user.save()
        
        # Actualizar información del perfil
        profile.nombre_completo = data.get('nombre_completo', profile.nombre_completo)
        profile.telefono = data.get('telefono', profile.telefono)
        profile.whatsapp = data.get('whatsapp', profile.whatsapp)
        profile.relacion_negocio = data.get('relacion_negocio', profile.relacion_negocio)
        profile.tipo_negocio = data.get('tipo_negocio', profile.tipo_negocio)
        profile.nombre_negocio = data.get('nombre_negocio', profile.nombre_negocio)
        profile.comuna = data.get('comuna', profile.comuna)
        profile.region = data.get('region', profile.region)
        profile.direccion = data.get('direccion', profile.direccion)
        profile.recibir_notificaciones = data.get('recibir_notificaciones', profile.recibir_notificaciones)
        profile.recibir_newsletter = data.get('recibir_newsletter', profile.recibir_newsletter)
        
        profile.save()
        
        return JsonResponse({
            "success": True,
            "message": "Perfil actualizado correctamente"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# --- Subir foto de perfil ---
@login_required
@csrf_exempt
def upload_profile_photo_api(request):
    """API para subir foto de perfil"""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if 'photo' not in request.FILES:
            return JsonResponse({
                "success": False,
                "error": "No se encontró ninguna imagen"
            }, status=400)
        
        photo = request.FILES['photo']
        
        # Validar tamaño (max 5MB)
        if photo.size > 5 * 1024 * 1024:
            return JsonResponse({
                "success": False,
                "error": "La imagen es demasiado grande. Máximo 5MB"
            }, status=400)
        
        # Validar formato
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = os.path.splitext(photo.name)[1].lower()
        if ext not in valid_extensions:
            return JsonResponse({
                "success": False,
                "error": "Formato no válido. Use: JPG, PNG, GIF o WEBP"
            }, status=400)
        
        # Eliminar foto anterior si existe
        if profile.foto_perfil:
            try:
                if os.path.isfile(profile.foto_perfil.path):
                    os.remove(profile.foto_perfil.path)
            except Exception:
                pass
        
        # Guardar nueva foto
        profile.foto_perfil = photo
        profile.save()
        
        return JsonResponse({
            "success": True,
            "message": "Foto actualizada correctamente",
            "photo_url": profile.foto_perfil.url
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# --- Eliminar foto de perfil ---
@login_required
@csrf_exempt
def delete_profile_photo_api(request):
    """API para eliminar foto de perfil"""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if profile.foto_perfil:
            try:
                if os.path.isfile(profile.foto_perfil.path):
                    os.remove(profile.foto_perfil.path)
            except Exception:
                pass
            profile.foto_perfil = None
            profile.save()
        
        return JsonResponse({
            "success": True,
            "message": "Foto eliminada correctamente"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# --- Cambiar contraseña ---
@login_required
@csrf_exempt
def change_password_api(request):
    """API para cambiar contraseña"""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verificar contraseña actual
        if not request.user.check_password(current_password):
            return JsonResponse({
                "success": False,
                "error": "La contraseña actual es incorrecta"
            }, status=400)
        
        # Validar nueva contraseña
        if len(new_password) < 6:
            return JsonResponse({
                "success": False,
                "error": "La contraseña debe tener al menos 6 caracteres"
            }, status=400)
        
        # Cambiar contraseña
        request.user.set_password(new_password)
        request.user.save()
        
        # Mantener la sesión activa
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({
            "success": True,
            "message": "Contraseña cambiada correctamente"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# --- Eliminar cuenta ---
@login_required
@csrf_exempt
def delete_account_api(request):
    """API para eliminar cuenta de usuario"""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        password = data.get('password')
        
        # Verificar contraseña
        if not request.user.check_password(password):
            return JsonResponse({
                "success": False,
                "error": "Contraseña incorrecta"
            }, status=400)
        
        # --- 2. LÍNEA AÑADIDA ---
        # Borra el historial de admin antes de borrar el usuario
        # Esto previene el error 'FOREIGN KEY constraint failed'
        LogEntry.objects.filter(user=request.user).delete()
        
        # Eliminar foto de perfil si existe
        if hasattr(request.user, 'profile') and request.user.profile.foto_perfil:
            try:
                if os.path.isfile(request.user.profile.foto_perfil.path):
                    os.remove(request.user.profile.foto_perfil.path)
            except Exception:
                pass
        
        # Eliminar usuario (esto también eliminará el perfil por CASCADE)
        username = request.user.username
        request.user.delete()
        
        return JsonResponse({
            "success": True,
            "message": f"La cuenta de {username} ha sido eliminada correctamente"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
        
        


# --- Vista del catálogo ---
@login_required
def catalog_view(request):
    products = Product.objects.all()
    return render(request, 'chatApp/catalog.html', {'products': products})


# --- Vista para descargas ---
@login_required
def download_view(request):
    return render(request, 'chatApp/download.html')


# =========================================
# 🔹 AUTENTICACIÓN | APIs usadas por main.js
# =========================================
@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"success": False, "error": "Email y contraseña son requeridos"}, status=400)

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Credenciales inválidas"}, status=400)

        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            return JsonResponse({"success": False, "error": "Credenciales inválidas"}, status=400)

        login(request, user)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "error": "Usuario ya existe"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)

        UserProfile.objects.get_or_create(user=user)

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    logout(request)
    return JsonResponse({"success": True})


# =========================================
# 🛒 CARRITO | APIs usadas por main.js
# =========================================
@login_required
def get_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    items = [
        {
            "nombre": item.product.name,
            "cantidad": item.quantity,
            "subtotal": item.product.price * item.quantity
        }
        for item in cart_items
    ]

    total = sum(item.product.price * item.quantity for item in cart_items)

    return JsonResponse({
        "items": items,
        "total": total
    })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({"success": True})
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Producto no encontrado"}, status=404)