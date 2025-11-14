"""
Sérialiseurs pour l'espace de discussion.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import ChatMessage, ChatThread

from .accounts import UserSummarySerializer

User = get_user_model()


class ChatMessageSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "thread",
            "author",
            "content",
            "attachment",
            "metadata",
            "is_deleted",
            "deleted_at",
            "created_at",
            "edited_at",
        )
        read_only_fields = (
            "author",
            "metadata",
            "is_deleted",
            "deleted_at",
            "created_at",
            "edited_at",
        )


class ChatThreadSerializer(serializers.ModelSerializer):
    participants = UserSummarySerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, many=True, required=False)
    created_by = UserSummarySerializer(read_only=True)
    last_message_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ChatThread
        fields = (
            "id",
            "title",
            "project",
            "is_private",
            "created_by",
            "participants",
            "participant_ids",
            "created_at",
            "updated_at",
            "last_message_at",
        )
        read_only_fields = (
            "created_by",
            "participants",
            "created_at",
            "updated_at",
            "last_message_at",
        )

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids", [])
        request = self.context["request"]
        thread = super().create(validated_data)
        participants = {user.pk: user for user in participant_ids}
        participants[request.user.pk] = request.user
        thread.participants.add(*participants.values())
        return thread

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop("participant_ids", None)
        thread = super().update(instance, validated_data)
        if participant_ids is not None:
            participants = {user.pk: user for user in participant_ids}
            request_user = self.context["request"].user
            participants[request_user.pk] = request_user
            thread.participants.set(participants.values())
        return thread

