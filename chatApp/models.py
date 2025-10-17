from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    TAB_CHOICES = [
        ('nacional', 'Nacional'),
        ('local', 'Local'),
        ('soporte', 'Soporte'),
        
    ]

    tab = models.CharField(max_length=10, choices=TAB_CHOICES, default='nacional')
    text = models.TextField()
    avatar = models.CharField(max_length=255, blank=True)  
    timestamp = models.DateTimeField(auto_now_add=True)
    # store the sender's username (optional)
    sender = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.get_tab_display()} - {self.text[:30]}"
    
    from django.contrib.auth.models import User
from django.db import models

class Product(models.Model):
    PRODUCT_TYPES = [
        ('individual', 'Software El Almacén - Punto de Venta 1 PC'),
        ('red', 'Software El Almacén en Red para 2 o 3 PC'),
        ('empresarial', 'Software El Almacén Empresarial Multi PC'),
    ]
    
    tipo = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    caracteristicas = models.JSONField(default=list)  # Lista de características
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    es_destacado = models.BooleanField(default=False)
    badge = models.CharField(max_length=50, blank=True, null=True)  # Para mostrar "RED" o "PREMIUM"

    def __str__(self):
        return self.nombre

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.precio * self.cantidad

