"""
Sérialiseur pour les journaux d'audit.
"""

from rest_framework import serializers

from core.models import AuditLog

from .accounts import UserSummarySerializer


class AuditLogSerializer(serializers.ModelSerializer):
    actor = UserSummarySerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"

