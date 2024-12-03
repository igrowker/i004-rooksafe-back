"""
ASGI config for site_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.candles.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_app.settings.local') # Modificar dependiendo local/production

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.candles.routing.websocket_urlpatterns
        )
    ),
})