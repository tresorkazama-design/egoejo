from rest_framework import mixins, viewsets, permissions

from core.models import Engagement
from core.serializers import EngagementSerializer


class EngagementViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API pour les engagements d'aide.

    DEV :
    - GET  /api/engagements/               : lister tous les engagements
      * ?help_request=<id>                 : engagements liés à une demande/projet
    - POST /api/engagements/               : créer un engagement
    """

    serializer_class = EngagementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Engagement.objects.all().order_by("-created_at")

        help_request_id = self.request.query_params.get("help_request")
        if help_request_id:
            qs = qs.filter(help_request_id=help_request_id)

        return qs


