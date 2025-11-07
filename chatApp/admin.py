from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id','tab','text','avatar','timestamp')
    list_filter = ('tab','timestamp')
    search_fields = ('text','avatar')