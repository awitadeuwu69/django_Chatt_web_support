"""
URL configuration for Chatglobal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from chatApp import views



urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('login/', views.login_api, name='login'),       
    path('register/', views.register_api, name='register'), 
    path('logout/', views.logout_api, name='logout'),
    path('messages/', views.messages_api, name='messages_api'),
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path("admin/", admin.site.urls),
]

