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

    def __str__(self):
        return f"{self.get_tab_display()} - {self.text[:30]}"
    
    from django.contrib.auth.models import User
from django.db import models

class Product(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.precio * self.cantidad

