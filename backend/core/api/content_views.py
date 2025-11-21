from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import EducationalContent
from core.serializers import EducationalContentSerializer


class EducationalContentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    - GET  /api/contents/                  : liste des contenus (filtrable par status)
      * ?status=published                  : contenus publiés
      * ?status=pending                    : contenus en attente
    - GET  /api/contents/{id}/             : détail
    - POST /api/contents/                  : proposer un contenu (status=pending)
    - POST /api/contents/{id}/publish/     : publier un contenu (status=published)
    """

    serializer_class = EducationalContentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = EducationalContent.objects.all().order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        author = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            author=author,
            status="pending",  # les contenus proposés vont en "en attente"
        )

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """
        Passe ce contenu en 'published'.
        """
        content = self.get_object()
        content.status = "published"
        content.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)



