from django.contrib import admin
from .models import Message, Product, CartItem, UserProfile

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id','tab','text','avatar','timestamp')
    list_filter = ('tab','timestamp')
    search_fields = ('text','avatar')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'cantidad', 'subtotal')
    list_filter = ('user', 'product')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre_completo', 'role', 'fecha_creacion')
    list_filter = ('role', 'region', 'comuna')
    search_fields = ('user__username', 'nombre_completo', 'nombre_negocio')
    ordering = ('-fecha_creacion',)