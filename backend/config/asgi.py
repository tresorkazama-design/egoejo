import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter  # noqa: E402


def websocket_application(scope):
    from channels.auth import AuthMiddlewareStack  # noqa: E402
    from channels.routing import URLRouter  # noqa: E402
    from core.routing import websocket_urlpatterns  # noqa: E402

    return AuthMiddlewareStack(URLRouter(websocket_urlpatterns))(scope)


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": websocket_application,
    }
)
