"""
Endpoints relatifs aux cagnottes et contributions.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.models import Cagnotte
from core.serializers import CagnotteSerializer


class CagnotteListCreate(generics.ListCreateAPIView):
    queryset = Cagnotte.objects.all().order_by("-created_at")
    serializer_class = CagnotteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def contribute(request, pk):  # noqa: D401 - endpoint désactivé
    """
    Endpoint placeholder jusqu'à implémentation du paiement sécurisé.
    """
    return Response({"detail": "Endpoint désactivé"}, status=status.HTTP_404_NOT_FOUND)

