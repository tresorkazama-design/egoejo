"""
Viewset pour la gestion des scrutins participatifs.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.models import Poll, PollBallot, PollOption
from core.serializers import PollSerializer, PollVoteSerializer

from .common import broadcast_to_group, build_voter_hash, log_action


def _ensure_owner(request, poll: Poll):
    if poll.created_by != request.user and not request.user.is_staff:
        raise PermissionDenied("Action réservée au créateur ou à un admin.")


class PollViewSet(viewsets.ModelViewSet):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = (
            Poll.objects.select_related("created_by", "project")
            .prefetch_related("options", "options__ballots")
            .order_by("-created_at")
        )
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        project_param = self.request.query_params.get("project")
        if project_param:
            queryset = queryset.filter(project_id=project_param)
        return queryset

    def _sync_options(self, poll: Poll, options_data):
        if options_data is None:
            return
        active_ids = []
        for idx, option in enumerate(options_data):
            label = option.get("label")
            if not label:
                continue
            position = option.get("position", idx)
            option_id = option.get("id")
            if option_id:
                poll_option = PollOption.objects.filter(poll=poll, pk=option_id).first()
                if poll_option:
                    poll_option.label = label
                    poll_option.position = position
                    poll_option.save(update_fields=["label", "position"])
                    active_ids.append(poll_option.pk)
                    continue
            new_option = PollOption.objects.create(
                poll=poll, label=label, position=position
            )
            active_ids.append(new_option.pk)
        PollOption.objects.filter(poll=poll).exclude(pk__in=active_ids).delete()

    def perform_create(self, serializer):
        poll = serializer.save(created_by=self.request.user)
        options = self.request.data.get("options")
        self._sync_options(poll, options)
        log_action(
            self.request.user,
            "poll_create",
            "poll",
            poll.pk,
            {"title": poll.title},
        )

    def perform_update(self, serializer):
        poll = serializer.instance
        _ensure_owner(self.request, poll)
        updated_poll = serializer.save()
        self._sync_options(updated_poll, self.request.data.get("options"))
        log_action(self.request.user, "poll_update", "poll", poll.pk)
        return updated_poll

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def open(self, request, pk=None):
        poll = self.get_object()
        _ensure_owner(request, poll)
        poll.status = Poll.STATUS_OPEN
        if poll.opens_at is None:
            poll.opens_at = timezone.now()
        poll.save(update_fields=["status", "opens_at"])
        broadcast_to_group(
            f"poll_{poll.pk}",
            "poll_update",
            PollSerializer(poll, context={"request": request}).data,
        )
        log_action(request.user, "poll_open", "poll", poll.pk)
        return Response(self.get_serializer(poll).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def close(self, request, pk=None):
        poll = self.get_object()
        _ensure_owner(request, poll)
        poll.status = Poll.STATUS_CLOSED
        poll.closes_at = timezone.now()
        poll.save(update_fields=["status", "closes_at"])
        broadcast_to_group(
            f"poll_{poll.pk}",
            "poll_update",
            PollSerializer(poll, context={"request": request}).data,
        )
        log_action(request.user, "poll_close", "poll", poll.pk)
        return Response(self.get_serializer(poll).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        poll = self.get_object()
        now = timezone.now()
        if poll.status != Poll.STATUS_OPEN:
            return Response({"detail": "Ce vote est fermé."}, status=status.HTTP_400_BAD_REQUEST)
        if poll.opens_at and poll.opens_at > now:
            return Response({"detail": "Ce vote n'est pas encore ouvert."}, status=status.HTTP_400_BAD_REQUEST)
        if poll.closes_at and poll.closes_at < now:
            return Response({"detail": "Ce vote est cloture."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PollVoteSerializer(data=request.data, context={"poll": poll})
        serializer.is_valid(raise_exception=True)
        option_ids = serializer.validated_data["options"]
        voter_hash = build_voter_hash(request, poll)

        PollBallot.objects.filter(poll=poll, voter_hash=voter_hash).exclude(option_id__in=option_ids).delete()

        for option_id in option_ids:
            option = poll.options.get(pk=option_id)
            metadata = {"ts": now.isoformat()}
            if not poll.is_anonymous:
                metadata["user_id"] = request.user.pk
            PollBallot.objects.update_or_create(
                poll=poll,
                option=option,
                voter_hash=voter_hash,
                defaults={"metadata": metadata},
            )

        broadcast_to_group(
            f"poll_{poll.pk}",
            "poll_update",
            PollSerializer(poll, context={"request": request}).data,
        )
        log_action(
            request.user,
            "poll_vote",
            "poll",
            poll.pk,
            {"options": option_ids, "hash": voter_hash},
        )
        return Response(self.get_serializer(poll).data)

