from django.db import migrations

def crear_productos_iniciales(apps, schema_editor):
    Product = apps.get_model('chatApp', 'Product')
    
    # Primero limpiamos los productos existentes
    Product.objects.all().delete()
    
    productos = [
        {
            'tipo': 'individual',
            'nombre': 'Software El Almacén - Punto de Venta 1 PC',
            'caracteristicas': [
                '01 Licencia de Usuario / 1 PC',
                'Manual en PDF',
                'Servicio de Instalación Remota Opcional',
                'Centro de Auto-soporte',
                'Plataforma de Minivideos de Capacitación',
                '1 Año de Soporte Personalizado sin Costo',
                'Whatsapp, WEB, E-mail, Soporte Remoto'
            ],
            'descripcion': 'Software para punto de venta individual',
            'precio': 0,
            'badge': '',
            'es_destacado': False
        },
        {
            'tipo': 'red',
            'nombre': 'Software El Almacén en Red para 2 o 3 PC',
            'caracteristicas': [
                '02 Licencias de Usuario / 2 o 3 PC',
                'Servicio de Configuración / RED',
                'Manual en PDF',
                'Servicio de Instalación Remota Opcional',
                'Centro de Auto-soporte',
                'Plataforma de Minivideos de Capacitación',
                '01 Año de Soporte Personalizado sin Costo',
                'Whatsapp, WEB, E-mail, Soporte Remoto'
            ],
            'descripcion': 'Software en red para múltiples puntos de venta',
            'precio': 0,
            'badge': 'RED',
            'es_destacado': True
        },
        {
            'tipo': 'empresarial',
            'nombre': 'Software El Almacén Empresarial Multi PC',
            'caracteristicas': [
                '3+ Licencias de Usuario / Multi PC',
                'Configuración de Red Avanzada',
                'Manual en PDF + Documentación Técnica',
                'Servicio de Instalación Remota Premium',
                'Centro de Auto-soporte Prioritario',
                'Plataforma de Capacitación Empresarial',
                '01 Año de Soporte Premium sin Costo',
                'Soporte 24/7 por Todos los Canales'
            ],
            'descripcion': 'Software empresarial con funcionalidades avanzadas',
            'precio': 0,
            'badge': 'PREMIUM',
            'es_destacado': False
        }
    ]
    
    for producto in productos:
        Product.objects.create(**producto)

def eliminar_productos(apps, schema_editor):
    Product = apps.get_model('chatApp', 'Product')
    Product.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('chatApp', '0004_product_badge_product_caracteristicas_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_productos_iniciales, eliminar_productos),
    ]