"""
Vues liées à la consultation des journaux d'audit.
"""

from rest_framework import permissions, viewsets

from core.models import AuditLog
from core.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return AuditLog.objects.select_related("actor").order_by("-created_at")

