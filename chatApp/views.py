# Agregar estos imports al inicio de tu views.py
import datetime
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import requests
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
from .models import BlogPost, Reaction, Comment
from django.db import models


from .youtube_service import get_youtube_events
from django.http import JsonResponse
from .models import BlogPost
from .forms import BlogPostForm
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test


def admin_required(function):
    """
    Decorator for views that require the user to be an administrator.
    """
    def wrap(request, *args, **kwargs):
        # Use Django's built-in superuser flag for admin access
        if request.user.is_authenticated and request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return redirect('chatApp:index')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


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
    # Count raw sessions not expired
    active_sessions = Session.objects.filter(
        expire_date__gte=timezone.now()).count()

    # Count unique logged-in users with active sessions
    session_qs = Session.objects.filter(expire_date__gte=timezone.now())
    user_ids = set()
    for s in session_qs:
        try:
            data = s.get_decoded()
            uid = data.get('_auth_user_id')
            if uid:
                user_ids.add(int(uid))
        except Exception:
            continue
    online_users_count = len(user_ids)

    # 3. IP pública (con caché simple)
    if public_ip_cache is None:
        try:
            response = requests.get(
                'https://api.ipify.org?format=json', timeout=5)
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
        user_profiles = user_profiles.filter(
            user__username__icontains=search_query)

    # Lógica de ordenamiento
    order_field = '-user__date_joined'  # Default
    if sort_by == 'date_asc':
        order_field = 'user__date_joined'
    elif sort_by == 'date_desc':
        order_field = '-user__date_joined'
    elif sort_by == 'role_asc':
        order_field = 'role'
    elif sort_by == 'role_desc':
        order_field = '-role'

    user_profiles = user_profiles.order_by(order_field)

    # Paginate user profiles
    page = request.GET.get('page', 1)
    paginator = Paginator(user_profiles, 20)  # 20 por página
    try:
        user_profiles_page = paginator.page(page)
    except PageNotAnInteger:
        user_profiles_page = paginator.page(1)
    except EmptyPage:
        user_profiles_page = paginator.page(paginator.num_pages)

    context = {
        'user_profiles': user_profiles_page,
        'search_query': search_query,
        'sort_by': sort_by,
        'master_panel': {
            'uptime': uptime_str,
            'active_sessions': active_sessions,
            'online_users': online_users_count,
            'public_ip': public_ip,
        }
    }

    # Include blog posts for the admin panel (management section)
    try:
        context['posts'] = BlogPost.objects.all()
    except Exception:
        context['posts'] = []

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
        messages.error(
            request, f"El perfil para el usuario '{username}' no fue encontrado.")
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


def club_blog_view(request):
    # Prefetch related objects to minimize queries
    posts = BlogPost.objects.filter(published=True).prefetch_related(
        'tags', 'comments__author', 'reactions__user', 'author')

    # For each post, compute counts for common emojis and whether the current user reacted
    EMOJIS = ['👍', '❤️', '😂', '🎉']
    for post in posts:
        counts = {e: 0 for e in EMOJIS}
        for r in post.reactions.all():
            if r.emoji in counts:
                counts[r.emoji] += 1
        # attach attributes for template convenience
        post.like_count = counts.get('👍', 0)
        post.heart_count = counts.get('❤️', 0)
        post.laugh_count = counts.get('😂', 0)
        post.party_count = counts.get('🎉', 0)

        if request.user.is_authenticated:
            user_emojis = set(post.reactions.filter(
                user=request.user).values_list('emoji', flat=True))
            post.user_like = '👍' in user_emojis
            post.user_heart = '❤️' in user_emojis
            post.user_laugh = '😂' in user_emojis
            post.user_party = '🎉' in user_emojis
        else:
            post.user_like = post.user_heart = post.user_laugh = post.user_party = False

    return render(request, 'chatApp/club_almacen_blog.html', {'posts': posts})


@login_required
def create_post_view(request):
    # only providers (role == 'proveedor') or superuser can create
    profile = getattr(request.user, 'profile', None)
    if not (request.user.is_superuser or (profile and profile.role == 'proveedor')):
        raise PermissionDenied()

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=True, author=request.user)
            return redirect('chatApp:club_almacen_blog')
    else:
        # prefill tags_input from GET maybe
        form = BlogPostForm()
    return render(request, 'chatApp/blog_post_form.html', {'form': form, 'action': 'Crear'})


@login_required
def edit_post_view(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    # only author or superuser can edit
    if not (request.user.is_superuser or post.author == request.user):
        raise PermissionDenied()

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(commit=True, author=request.user)
            return redirect('chatApp:club_almacen_blog')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'chatApp/blog_post_form.html', {'form': form, 'action': 'Editar', 'post': post})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if not (request.user.is_superuser or post.author == request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        post.delete()
        return redirect('chatApp:club_almacen_blog')
    return render(request, 'chatApp/blog_post_confirm_delete.html', {'post': post})


@login_required
@require_http_methods(["POST"])
def add_comment_api(request, pk):
    try:
        post = BlogPost.objects.get(pk=pk)
    except BlogPost.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post no encontrado'}, status=404)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        if not content:
            return JsonResponse({'success': False, 'error': 'Contenido vacío'}, status=400)

        comment = post.comments.create(author=request.user, content=content)
        return JsonResponse({'success': True, 'comment': {
            'id': comment.id,
            'author': comment.author.username if comment.author else 'Anon',
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        }})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def edit_comment_api(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comentario no encontrado'}, status=404)

    # authorization: only author or superuser
    if not (request.user.is_superuser or comment.author == request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        if not content:
            return JsonResponse({'success': False, 'error': 'Contenido vacío'}, status=400)
        comment.content = content
        comment.save()
        return JsonResponse({'success': True, 'comment': {
            'id': comment.id,
            'author': comment.author.username if comment.author else 'Anon',
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        }})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_comment_api(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comentario no encontrado'}, status=404)

    if not (request.user.is_superuser or comment.author == request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    try:
        comment.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def add_reaction_api(request, pk):
    try:
        post = BlogPost.objects.get(pk=pk)
    except BlogPost.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post no encontrado'}, status=404)

    try:
        data = json.loads(request.body)
        emoji = data.get('emoji')
        if not emoji:
            return JsonResponse({'success': False, 'error': 'Emoji requerido'}, status=400)

        # toggle reaction: if exists, remove; else create
        obj, created = Reaction.objects.get_or_create(
            post=post, user=request.user, emoji=emoji)
        if not created:
            obj.delete()
            action = 'removed'
        else:
            action = 'added'

        # return counts per emoji
        counts = {}
        for r in post.reactions.values('emoji').order_by().annotate(count=models.Count('id')):
            counts[r['emoji']] = r['count']

        return JsonResponse({'success': True, 'action': action, 'counts': counts})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# NOTE: the full `admin_dashboard` implementation is defined earlier (with master_panel and user_profiles)
# the simple fallback implementation was removed to keep the detailed dashboard with stats and user list.


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
        profile.nombre_completo = data.get(
            'nombre_completo', profile.nombre_completo)
        profile.telefono = data.get('telefono', profile.telefono)
        profile.whatsapp = data.get('whatsapp', profile.whatsapp)
        profile.relacion_negocio = data.get(
            'relacion_negocio', profile.relacion_negocio)
        profile.tipo_negocio = data.get('tipo_negocio', profile.tipo_negocio)
        profile.nombre_negocio = data.get(
            'nombre_negocio', profile.nombre_negocio)
        profile.comuna = data.get('comuna', profile.comuna)
        profile.region = data.get('region', profile.region)
        profile.direccion = data.get('direccion', profile.direccion)
        profile.recibir_notificaciones = data.get(
            'recibir_notificaciones', profile.recibir_notificaciones)
        profile.recibir_newsletter = data.get(
            'recibir_newsletter', profile.recibir_newsletter)

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
def catalog_view(request):
    products = Product.objects.all()
    return render(request, 'chatApp/catalog.html', {'products': products})


# --- Vista para descargas ---
def download_view(request):
    return render(request, 'chatApp/download.html')


# --- Vista para el blog de Club Almacén ---
def club_almacen_blog_view(request):
    return render(request, 'chatApp/club_almacen_blog.html')


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

        user = authenticate(
            request, username=user_obj.username, password=password)

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

        user = User.objects.create_user(
            username=username, password=password, email=email)

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

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product)
        cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({"success": True})
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Producto no encontrado"}, status=404)

        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product)
        cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({"success": True})
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Producto no encontrado"}, status=404)
