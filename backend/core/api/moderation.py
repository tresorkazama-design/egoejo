"""
Vues pour la modération et le suivi des signalements.
"""

from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from core.models import ModerationReport
from core.serializers import ModerationReportSerializer

from .common import log_action


class ModerationReportViewSet(viewsets.ModelViewSet):
    serializer_class = ModerationReportSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = ModerationReport.objects.select_related("reporter", "resolved_by").order_by("-created_at")
        if user.is_staff:
            return base_qs
        if user.is_authenticated:
            return base_qs.filter(reporter=user)
        return ModerationReport.objects.none()

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        report = serializer.save(reporter=self.request.user)
        log_action(
            self.request.user,
            "moderation_report_create",
            "moderation_report",
            report.pk,
            {"type": report.report_type, "target_id": report.target_id},
        )

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Action reservee aux moderateurs.")
        report = serializer.save()
        if report.status != ModerationReport.STATUS_PENDING and report.resolved_by_id != self.request.user.pk:
            report.resolved_by = self.request.user
            report.save(update_fields=["resolved_by"])
        log_action(
            self.request.user,
            "moderation_report_update",
            "moderation_report",
            serializer.instance.pk,
            {"status": report.status},
        )

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Action reservee aux moderateurs.")
        target_id = instance.pk
        instance.delete()
        log_action(self.request.user, "moderation_report_delete", "moderation_report", target_id)

