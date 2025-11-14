"""
Sérialiseurs liés aux utilisateurs et profils.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import Profile

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "display_name",
            "bio",
            "avatar",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

