import os
from channels.auth import AuthMiddlewareStack
# from websocket.middlewares import WebSocketJWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from index import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
                )
            ),
    }
)