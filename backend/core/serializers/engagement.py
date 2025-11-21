from rest_framework import serializers
from core.models import Engagement


class EngagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engagement
        fields = [
            "id",
            "help_types",
            "domains",
            "availability",
            "scope",
            "anonymity",
            "notes",
            "help_request",   # ✅ lien vers HelpRequest
            "status",
            "created_at",
        ]
        read_only_fields = ("status", "created_at")

