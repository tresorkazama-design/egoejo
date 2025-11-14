import os
import logging

from django.core.asgi import get_asgi_application

# Configure le logging avant tout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

logger.info("Initializing Django ASGI application...")
django_asgi_app = get_asgi_application()
logger.info("Django ASGI application initialized")

from channels.routing import ProtocolTypeRouter  # noqa: E402


def websocket_application(scope):
    """Application WebSocket pour Channels"""
    try:
        from channels.auth import AuthMiddlewareStack  # noqa: E402
        from channels.routing import URLRouter  # noqa: E402
        from core.routing import websocket_urlpatterns  # noqa: E402

        return AuthMiddlewareStack(URLRouter(websocket_urlpatterns))(scope)
    except ImportError as e:
        logger.error(f"Failed to import WebSocket dependencies: {e}")
        # Retourner une application vide en cas d'erreur
        async def empty_websocket(scope, receive, send):
            await send({"type": "websocket.close"})
        return empty_websocket
    except Exception as e:
        logger.error(f"Error in websocket_application: {e}")
        raise


logger.info("Initializing ASGI ProtocolTypeRouter...")
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": websocket_application,
    }
)
logger.info("ASGI application ready")
