from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import HelpRequest
from core.serializers import HelpRequestSerializer


class HelpRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API pour les demandes d'aide.

    DEV :
    - GET  /api/help-requests/                      : lister toutes les demandes
      * filtre ?status=accepted                     : seulement les demandes acceptées (projets)
      * filtre ?mine=1 (si connecté)               : seulement mes demandes
    - POST /api/help-requests/                      : créer une demande
    - POST /api/help-requests/{id}/mark-as-project/ : marquer une demande comme projet (status=accepted)
    """

    serializer_class = HelpRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = HelpRequest.objects.all().order_by("-created_at")

        # Filtrer par statut (ex: status=accepted pour les projets)
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        # Filtrer "mes demandes" si le user est authentifié et mine=1
        mine = self.request.query_params.get("mine")
        if mine in ("1", "true", "yes") and self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)

        return qs

    def perform_create(self, serializer):
        """
        Si l'utilisateur est connecté, on attache la demande à ce user.
        Sinon, user=None.
        """
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    @action(detail=True, methods=["post"], url_path="mark-as-project")
    def mark_as_project(self, request, pk=None):
        """
        Marque cette demande comme "acceptée" (projet EGOEJO).
        """
        help_request = self.get_object()
        help_request.status = "accepted"
        help_request.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(help_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


