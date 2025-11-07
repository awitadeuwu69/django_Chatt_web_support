from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chatApp import views

urlpatterns = [
    # API de autenticación
    path('login/', views.login_api, name='login'),
    path('register/', views.register_api, name='register'),
    path('logout/', views.logout_api, name='logout'),

    # Carrito
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),

    # Rutas de la aplicación de chat (chat, messages, catalog, download)
    path('', include('chatApp.urls')),

    # Admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

