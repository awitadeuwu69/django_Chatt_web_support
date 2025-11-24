"""
Script para crear un usuario de prueba para el blog
Ejecutar con: python create_test_user.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chatglobal.settings')
django.setup()

from django.contrib.auth.models import User
from chatApp.models import UserProfile

def create_test_user():
    """Crea un usuario de prueba si no existe"""
    
    # Usuario normal
    username = "usuario_prueba"
    email = "prueba@test.com"
    password = "prueba123"
    
    # Verificar si ya existe
    if User.objects.filter(username=username).exists():
        print(f"El usuario '{username}' ya existe.")
        user = User.objects.get(username=username)
        print(f"Puedes usar: username={username}, password={password}")
    else:
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"Usuario '{username}' creado exitosamente!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    
    # Crear perfil si no existe
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        print(f"Perfil creado para '{username}'")
    
    print("\n" + "="*50)
    print("CREDENCIALES DE PRUEBA:")
    print("="*50)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("="*50)
    
def create_admin_user():
    """Crea un superusuario de prueba si no existe"""
    
    username = "admin"
    email = "admin@test.com"
    password = "admin123"
    
    if User.objects.filter(username=username).exists():
        print(f"\nEl superusuario '{username}' ya existe.")
        print(f"Puedes usar: username={username}, password={password}")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"\nSuperusuario '{username}' creado exitosamente!")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        
        # Crear perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            print(f"Perfil creado para '{username}'")
    
    print("\n" + "="*50)
    print("CREDENCIALES DE ADMIN:")
    print("="*50)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("="*50)

if __name__ == '__main__':
    print("\nCreando usuarios de prueba...\n")
    create_test_user()
    create_admin_user()
    print("\nListo! Ahora puedes iniciar sesión con cualquiera de estos usuarios.\n")
