from django.urls import path
from . import views

app_name = 'chatApp'
urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('messages/', views.messages_api, name='messages_api'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('download/', views.download_view, name='download'),
]
