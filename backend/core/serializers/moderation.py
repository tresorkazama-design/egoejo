"""
Sérialiseurs pour les signalements de modération.
"""

from rest_framework import serializers

from core.models import ModerationReport

from .accounts import UserSummarySerializer


class ModerationReportSerializer(serializers.ModelSerializer):
    reporter = UserSummarySerializer(read_only=True)
    resolved_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = ModerationReport
        fields = "__all__"

