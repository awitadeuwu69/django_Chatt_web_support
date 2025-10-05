import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from .models import Message

def chat_view(request):
    # Avatares predefinidos en static/chatApp/avatars/
    avatars = [
        static('images/avatars/avatar1.png'),
        static('images/avatars/avatar2.png'),
        static('images/avatars/avatar3.png'),
    ]
    return render(request, 'chatApp/index.html', {'avatars': avatars})

@require_http_methods(["GET", "POST"])
def messages_api(request):
    if request.method == 'GET':
        tab = request.GET.get('tab', 'nacional')
        msgs = Message.objects.filter(tab=tab).order_by('timestamp')
        data = [{
            'id': m.id,
            'text': m.text,
            'avatar': m.avatar,
            'timestamp': m.timestamp.strftime('%d/%m/%Y %H:%M')
        } for m in msgs]
        return JsonResponse({'messages': data})

    # POST → guardar mensaje
    try:
        payload = json.loads(request.body.decode('utf-8'))
        text = payload.get('text', '').strip()
        tab = payload.get('tab', 'nacional')
        avatar = payload.get('avatar', '')
        if not text:
            return HttpResponseBadRequest('Mensaje vacío')
        m = Message.objects.create(text=text, tab=tab, avatar=avatar)
        return JsonResponse({'message': {
            'id': m.id,
            'text': m.text,
            'avatar': m.avatar,
            'timestamp': m.timestamp.strftime('%d/%m/%Y %H:%M')
        }})
    except Exception as e:
        return HttpResponseBadRequest(str(e))
