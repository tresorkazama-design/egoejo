"""
Viewset pour la gestion des scrutins participatifs.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.models import Poll, PollBallot, PollOption
from core.models.polls import compute_quadratic_weight
from core.serializers import PollSerializer, PollVoteSerializer
from core.services.saka import harvest_saka, spend_saka, SakaReason
from django.conf import settings

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
        voter_hash = build_voter_hash(request, poll)
        option_ids = []  # Pour log_action
        votes_data = []  # Pour log_action
        rankings_data = []  # Pour log_action
        saka_spent = 0  # Initialiser pour tous les cas
        saka_cost = 0
        intensity = 1
        weight = 1.0

        # Gérer selon la méthode de vote
        if poll.voting_method == 'quadratic':
            # Vote Quadratique : points distribués avec boost SAKA (Phase 2)
            votes_data = request.data.get("votes", [])  # [{option_id: 1, points: 25, intensity: 3}, ...]
            max_points = poll.max_points or 100
            total_points = sum(v.get('points', 0) for v in votes_data)
            
            if total_points > max_points:
                return Response({
                    "detail": f"Total de points ({total_points}) dépasse le maximum ({max_points})"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer l'intensité globale du vote (ou calculer depuis les votes individuels)
            intensity = int(request.data.get("intensity", 1))
            intensity = max(1, min(intensity, 5))  # Clamp 1-5
            
            # Calculer le coût SAKA
            saka_cost_per = getattr(settings, "SAKA_VOTE_COST_PER_INTENSITY", 5)
            saka_cost = intensity * saka_cost_per
            saka_spent = 0
            
            # Tenter de dépenser les SAKA si activé
            if getattr(settings, "ENABLE_SAKA", False) and getattr(settings, "SAKA_VOTE_ENABLED", False):
                if spend_saka(
                    request.user,
                    saka_cost,
                    reason="poll_boost",
                    metadata={"poll_id": poll.id, "intensity": intensity}
                ):
                    saka_spent = saka_cost
            
            # Calculer le poids quadratique avec boost SAKA
            weight = compute_quadratic_weight(intensity=intensity, saka_spent=saka_spent)
            
            # Supprimer les anciens votes
            PollBallot.objects.filter(poll=poll, voter_hash=voter_hash).delete()
            
            # Créer les nouveaux votes avec points, poids et SAKA
            for vote_data in votes_data:
                option_id = vote_data.get('option_id')
                points = vote_data.get('points', 0)
                if points > 0:
                    option = poll.options.get(pk=option_id)
                    metadata = {"ts": now.isoformat(), "points": points, "intensity": intensity}
                    if not poll.is_anonymous:
                        metadata["user_id"] = request.user.pk
                    PollBallot.objects.create(
                        poll=poll,
                        option=option,
                        voter_hash=voter_hash,
                        points=points,
                        weight=weight,
                        saka_spent=saka_spent,
                        metadata=metadata,
                    )
                    option_ids.append(option_id)
        
        elif poll.voting_method == 'majority':
            # Jugement Majoritaire : classement
            rankings_data = request.data.get("rankings", [])  # [{option_id: 1, ranking: 1}, ...]
            
            # Supprimer les anciens votes
            PollBallot.objects.filter(poll=poll, voter_hash=voter_hash).delete()
            
            # Créer les votes avec classement
            for rank_data in rankings_data:
                option_id = rank_data.get('option_id')
                ranking = rank_data.get('ranking')
                option = poll.options.get(pk=option_id)
                metadata = {"ts": now.isoformat(), "ranking": ranking}
                if not poll.is_anonymous:
                    metadata["user_id"] = request.user.pk
                PollBallot.objects.create(
                    poll=poll,
                    option=option,
                    voter_hash=voter_hash,
                    ranking=ranking,
                    metadata=metadata,
                )
                option_ids.append(option_id)
        
        else:
            # Vote Binaire (défaut)
            option_ids = serializer.validated_data["options"]
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
        # Log action avec les bonnes données selon la méthode
        log_data = {"hash": voter_hash}
        if poll.voting_method == 'quadratic':
            log_data["votes"] = votes_data
        elif poll.voting_method == 'majority':
            log_data["rankings"] = rankings_data
        else:
            log_data["options"] = option_ids
        
        log_action(
            request.user,
            "poll_vote",
            "poll",
            poll.pk,
            log_data,
        )
        
        # Récolter des grains SAKA (Civic Mining) - Phase 1
        if request.user.is_authenticated:
            harvest_saka(
                user=request.user,
                reason=SakaReason.POLL_VOTE,
                metadata={'poll_id': poll.id, 'voting_method': poll.voting_method}
            )
        
        # Préparer la réponse avec les informations SAKA (Phase 2)
        response_data = self.get_serializer(poll).data
        
        if poll.voting_method == 'quadratic':
            # Ajouter les informations SAKA dans la réponse
            response_data['saka_info'] = {
                'saka_spent': saka_spent,
                'saka_cost': saka_cost,
                'intensity': intensity,
                'weight': weight,
            }
        
        return Response(response_data)

