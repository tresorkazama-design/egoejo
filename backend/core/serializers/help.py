from rest_framework import serializers
from core.models import HelpRequest


class HelpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpRequest
        fields = [
            "id",
            "title",
            "description",
            "help_type",
            "urgency",
            "is_linked_to_project",
            "project",
            "anonymity",
            "status",
            "created_at",
        ]
        read_only_fields = ("status", "created_at")
