from django.urls import path
from . import views

app_name = 'chatApp'
urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('messages/', views.messages_api, name='messages_api'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('download/', views.download_view, name='download'),
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('auth/login/', views.login_api, name='login_api'),
    path('auth/register/', views.register_api, name='register_api'),
    # backward-compatible aliases (some frontend code used these)
    path('login/', views.login_api, name='login_api_alias'),
    path('register/', views.register_api, name='register_api_alias'),
    path('logout/', views.logout_api, name='logout_api'),
]
