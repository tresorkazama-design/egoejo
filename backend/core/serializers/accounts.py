from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models.accounts import Profile

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used inside other serializers
    (for example: fundraising, contributions, etc.).
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "display_name", "bio", "avatar"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Simple registration serializer:
    - accepts username, email, password, first_name, last_name
    - hashes password and creates a Profile for the user
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.get_or_create(user=user)
        return user


class CurrentUserSerializer(UserSerializer):
    """
    Alias used by "current user" endpoints.
    """
    pass
