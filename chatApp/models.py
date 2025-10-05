from django.db import models

class Message(models.Model):
    TAB_CHOICES = [
        ('nacional', 'Nacional'),
        ('local', 'Local'),
        ('soporte', 'Soporte'),
        
    ]

    tab = models.CharField(max_length=10, choices=TAB_CHOICES, default='nacional')
    text = models.TextField()
    avatar = models.CharField(max_length=255, blank=True)  # ruta de imagen en static
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tab_display()} - {self.text[:30]}"
