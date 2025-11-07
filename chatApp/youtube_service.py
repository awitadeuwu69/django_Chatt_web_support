
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
from google.oauth2.credentials import Credentials
import json

# Permisos necesarios para YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_credentials():
    creds = None
    # Verifica si ya tenemos credenciales guardadas
    token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Chatglobal', 'token.json')
    if os.path.exists(token_path):
        with open(token_path, 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token))
    
    # Si no hay credenciales válidas, inicia el flujo de autenticación
    if not creds or not creds.valid:
        # Usar la ruta absoluta al archivo oauth_client_secret.json
        oauth_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Chatglobal', 'oauth_client_secret.json')
        flow = InstalledAppFlow.from_client_secrets_file(
            oauth_path, 
            SCOPES
        )
        creds = flow.run_local_server(port=8081)


        # Guarda las credenciales para el siguiente uso
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_youtube_events():
    try:
        creds = get_credentials()
    except Exception as e:
        print(f"Error en la autenticación: {e}")
        # Si hay error de autenticación, usa el comportamiento por defecto
        return [
            {
                'title': 'Evento de Muestra 1',
                'description': 'Esta es una descripción de un evento de muestra.',
                'thumbnail': 'https://via.placeholder.com/480x360.png?text=Evento+1',
                'url': '#'
            },
            {
                'title': 'Evento de Muestra 2',
                'description': 'Esta es una descripción de un evento de muestra.',
                'thumbnail': 'https://via.placeholder.com/480x360.png?text=Evento+2',
                'url': '#'
            },
            {
                'title': 'Evento de Muestra 3',
                'description': 'Esta es una descripción de un evento de muestra.',
                'thumbnail': 'https://via.placeholder.com/480x360.png?text=Evento+3',
                'url': '#'
            }
        ]

    # Crear el cliente de YouTube con las credenciales OAuth
    youtube = build('youtube', 'v3', credentials=creds)

    
    # ID del video específico que quieres mostrar. Puedes setearlo con la variable de entorno YOUTUBE_VIDEO_ID
    video_id = os.environ.get('YOUTUBE_VIDEO_ID', 'qfrJgeInMmE')
    try:
        # Solicitar también el 'status' para saber si el video es embebible
        video_request = youtube.videos().list(
            part='snippet,contentDetails,statistics,status',
            id=video_id
        )
        video_response = video_request.execute()
        
        if not video_response.get('items'):
            return []

        videos = []
        if video_response.get('items'):
            video = video_response['items'][0]
            video_snippet = video.get('snippet', {})

            # URLs for page and embed (use embed in iframes)
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            # Usar el dominio youtube-nocookie para mejorar privacidad
            site_origin = os.environ.get('SITE_ORIGIN','http://127.0.0.1:8000/' )
            embed_base = f'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1&playsinline=1'
            if site_origin:
                embed_url = embed_base + f'&origin={site_origin}'
                print("Embed URL final:", embed_url)

            else:
                embed_url = embed_base

            # Revisar status para saber si el video permite embeber
            status = video.get('status', {})
            embeddable = status.get('embeddable', True)
            privacy_status = status.get('privacyStatus', '')

            # safe thumbnail access with fallbacks
            thumbnails = video_snippet.get('thumbnails', {})
            thumbnail = (
                thumbnails.get('high', {}) .get('url')
                or thumbnails.get('medium', {}).get('url')
                or thumbnails.get('default', {}).get('url')
                or ''
            )

            videos.append({
                'title': video_snippet.get('title', ''),
                'description': video_snippet.get('description', ''),
                'thumbnail': thumbnail,
                'url': video_url,
                'embed_url': embed_url,
                'embed_allowed': bool(embeddable),
                'privacy_status': privacy_status,
                'embed_error': None if embeddable else 'El propietario del video ha deshabilitado el embeber.'
            })

        return videos

    except Exception as e:
        print(f'Error fetching YouTube events: {e}')
        return []
