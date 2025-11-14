"""
Sérialiseurs dédiés aux intentions.
"""

from rest_framework import serializers

from core.models import Intent


class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = "__all__"
        read_only_fields = ["ip", "user_agent", "created_at"]

