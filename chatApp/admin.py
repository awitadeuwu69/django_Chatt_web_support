from django.contrib import admin
from .models import Message, Product, CartItem, UserProfile, BlogPost, Tag, Comment, Reaction


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'tab', 'text', 'avatar', 'timestamp')
    list_filter = ('tab', 'timestamp')
    search_fields = ('text', 'avatar')


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


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'emoji', 'user', 'created_at')
    search_fields = ('post__title', 'user__username', 'emoji')
