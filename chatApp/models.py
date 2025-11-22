from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Message(models.Model):
    TAB_CHOICES = [
        ('nacional', 'Nacional'),
        ('local', 'Local'),
        ('soporte', 'Soporte'),
    ]

    tab = models.CharField(
        max_length=10, choices=TAB_CHOICES, default='nacional')
    text = models.TextField()
    avatar = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.get_tab_display()} - {self.text[:30]}"


class Product(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class CartItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.precio * self.cantidad


class UserProfile(models.Model):
    """Perfil extendido del usuario"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')

    # Roles
    ROLE_CHOICES = (
        ('user', 'Usuario'),
        ('admin', 'Administrador'),
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='user')

    # Información personal
    nombre_completo = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)

    # Información del negocio
    relacion_negocio = models.CharField(max_length=50, blank=True, choices=[
        ('dueno', 'Dueño'),
        ('conyuge', 'Cónyuge'),
        ('hijo', 'Hijo/a'),
        ('trabajador', 'Trabajador'),
    ])
    tipo_negocio = models.CharField(max_length=50, blank=True, choices=[
        ('almacen', 'Almacén'),
        ('minimarket', 'Minimarket'),
        ('botilleria', 'Botillería'),
        ('panaderia', 'Panadería'),
        ('ferreteria', 'Ferretería'),
        ('farmacia', 'Farmacia'),
        ('bazar', 'Bazar'),
        ('otro', 'Otro'),
    ])
    nombre_negocio = models.CharField(max_length=200, blank=True)

    # Ubicación
    comuna = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=300, blank=True)

    # Foto de perfil
    foto_perfil = models.ImageField(
        upload_to='profiles/', blank=True, null=True)

    # Configuración
    recibir_notificaciones = models.BooleanField(default=True)
    recibir_newsletter = models.BooleanField(default=True)

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    # Rol del usuario en la plataforma
    ROLE_CHOICES = [
        ('comerciante', 'Comerciante'),
        ('proveedor', 'Proveedor'),
    ]
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='comerciante')

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"


# Signal para crear perfil automáticamente cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.title} - {self.author.username}"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author or 'Anon'} on {self.post.title}"


class Reaction(models.Model):
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('post', 'user', 'emoji'),)

    def __str__(self):
        return f"{self.emoji} by {self.user or 'Anon'} on {self.post.title}"
