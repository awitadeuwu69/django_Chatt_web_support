from django.urls import path
from . import views

app_name = 'chatApp'

urlpatterns = [
    # Páginas principales
    path('', views.index_view, name='index'),

    path('catalog/', views.catalog_view, name='catalog'),
    path('download/', views.download_view, name='download'),
    path('profile/', views.profile_view, name='profile'),
    
    # API de mensajes
    #path('messages/', views.messages_api, name='messages_api'),
    
    # API de autenticación
    path('register/', views.register_api, name='register'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.logout_api, name='logout'),
    
    # API de carrito
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    
    # API de perfil
    path('api/profile/update/', views.update_profile_api, name='update_profile'),
    path('api/profile/upload-photo/', views.upload_profile_photo_api, name='upload_photo'),
    path('api/profile/delete-photo/', views.delete_profile_photo_api, name='delete_photo'),
    path('api/profile/change-password/', views.change_password_api, name='change_password'),
    path('api/profile/delete-account/', views.delete_account_api, name='delete_account'),
    path('update_events/', views.update_events_api, name='update_events'),
]