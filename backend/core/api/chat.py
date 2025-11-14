"""
Viewsets pour la messagerie instantanée.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.models import ChatMessage, ChatThread
from core.serializers import ChatMessageSerializer, ChatThreadSerializer

from .common import broadcast_to_group, log_action


class ChatThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ChatThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return ChatThread.objects.none()
        return (
            ChatThread.objects.filter(participants=user)
            .select_related("created_by", "project")
            .prefetch_related("participants")
        )

    def perform_create(self, serializer):
        thread = serializer.save(created_by=self.request.user)
        thread.last_message_at = timezone.now()
        thread.save(update_fields=["last_message_at"])
        log_action(
            self.request.user,
            "chat_thread_create",
            "chat_thread",
            thread.pk,
            {"title": thread.title},
        )

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.created_by != user and not user.is_staff:
            raise PermissionDenied("Suppression réservée au créateur ou à un admin.")
        target_id = instance.pk
        instance.delete()
        log_action(user, "chat_thread_delete", "chat_thread", target_id)


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return ChatMessage.objects.none()
        queryset = ChatMessage.objects.filter(thread__participants=user)
        thread_id = self.request.query_params.get("thread")
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        return queryset.select_related("author", "thread").order_by("created_at")

    def perform_create(self, serializer):
        thread = serializer.validated_data["thread"]
        if not thread.participants.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied("Vous ne participez pas à ce fil.")
        message = serializer.save(author=self.request.user)
        thread.last_message_at = timezone.now()
        thread.save(update_fields=["last_message_at"])
        data = ChatMessageSerializer(message, context={"request": self.request}).data
        broadcast_to_group(f"chat_thread_{thread.pk}", "chat_message", data)
        log_action(
            self.request.user,
            "chat_message_create",
            "chat_message",
            message.pk,
            {"thread": thread.pk},
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_staff:
            raise PermissionDenied("Modification reservee a l'auteur ou a un admin.")
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(edited_at=timezone.now())
        broadcast_to_group(
            f"chat_thread_{instance.thread_id}",
            "chat_message",
            ChatMessageSerializer(instance, context={"request": request}).data,
        )
        log_action(request.user, "chat_message_update", "chat_message", instance.pk)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_staff:
            raise PermissionDenied("Suppression reservee a l'auteur ou a un admin.")
        instance.delete()
        broadcast_to_group(
            f"chat_thread_{instance.thread_id}",
            "chat_message",
            ChatMessageSerializer(instance, context={"request": request}).data,
        )
        log_action(request.user, "chat_message_delete", "chat_message", instance.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

