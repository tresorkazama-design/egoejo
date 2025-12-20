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

# OPTIMISATION CPU : Cache des settings au niveau du module pour éviter les accès répétés
# Ces valeurs sont calculées une seule fois au démarrage du module
_SAKA_VOTE_COST_PER_INTENSITY = getattr(settings, "SAKA_VOTE_COST_PER_INTENSITY", 5)
_ENABLE_SAKA = getattr(settings, "ENABLE_SAKA", False)
_SAKA_VOTE_ENABLED = getattr(settings, "SAKA_VOTE_ENABLED", False)


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
        """
        Synchronise les options d'un poll avec les données fournies.
        
        OPTIMISATION N+1 : Utilise bulk_create et bulk_update au lieu de create/save individuels.
        ÉRADICATION N+1 : Utilise prefetch_related pour éviter les requêtes supplémentaires.
        """
        if options_data is None:
            return
        
        # ÉRADICATION N+1 : Récupérer toutes les options existantes en une seule requête
        # Utiliser prefetch_related si poll.options est déjà préchargé, sinon une seule requête
        existing_option_ids = [opt.get("id") for opt in options_data if opt.get("id")]
        if existing_option_ids:
            # Si poll.options est déjà préchargé (via prefetch_related), utiliser directement
            if hasattr(poll, '_prefetched_objects_cache') and 'options' in poll._prefetched_objects_cache:
                existing_options = {
                    opt.id: opt 
                    for opt in poll.options.all() if opt.id in existing_option_ids
                }
            else:
                # Sinon, une seule requête avec filter
                existing_options = {
                    opt.id: opt 
                    for opt in PollOption.objects.filter(poll=poll, pk__in=existing_option_ids)
                }
        else:
            existing_options = {}
        
        # Préparer les listes pour bulk operations
        options_to_update = []
        options_to_create = []
        active_ids = []
        
        for idx, option in enumerate(options_data):
            label = option.get("label")
            if not label:
                continue
            position = option.get("position", idx)
            option_id = option.get("id")
            
            if option_id and option_id in existing_options:
                # Option existante à mettre à jour
                poll_option = existing_options[option_id]
                poll_option.label = label
                poll_option.position = position
                options_to_update.append(poll_option)
                active_ids.append(poll_option.pk)
            else:
                # Nouvelle option à créer
                options_to_create.append(
                    PollOption(poll=poll, label=label, position=position)
                )
        
        # OPTIMISATION N+1 : Bulk operations au lieu de create/save individuels
        if options_to_update:
            PollOption.objects.bulk_update(options_to_update, ['label', 'position'], batch_size=100)
            active_ids.extend([opt.pk for opt in options_to_update])
        
        if options_to_create:
            created_options = PollOption.objects.bulk_create(options_to_create, batch_size=100)
            active_ids.extend([opt.pk for opt in created_options])
        
        # Supprimer les options qui ne sont plus dans la liste
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
        # ÉRADICATION N+1 : Précharger les options avant le vote
        poll = self.get_object()
        # S'assurer que les options sont préchargées pour éviter les requêtes supplémentaires
        if not hasattr(poll, '_prefetched_objects_cache') or 'options' not in poll._prefetched_objects_cache:
            poll = Poll.objects.prefetch_related('options').get(pk=poll.pk)
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
            
            # OPTIMISATION CPU : Utiliser les valeurs cachées au niveau du module
            saka_cost = intensity * _SAKA_VOTE_COST_PER_INTENSITY
            saka_spent = 0
            
            # OPTIMISATION CPU : Utiliser les valeurs cachées au niveau du module
            if _ENABLE_SAKA and _SAKA_VOTE_ENABLED:
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
            
            # ÉRADICATION N+1 : Récupérer toutes les options en une seule fois
            # Utiliser prefetch_related si poll.options est déjà préchargé
            option_ids_to_fetch = [v.get('option_id') for v in votes_data if v.get('points', 0) > 0]
            if hasattr(poll, '_prefetched_objects_cache') and 'options' in poll._prefetched_objects_cache:
                # Options déjà préchargées, filtrer en Python
                options_map = {
                    opt.id: opt 
                    for opt in poll.options.all() if opt.id in option_ids_to_fetch
                }
            else:
                # Sinon, une seule requête avec filter
                options_map = {
                    opt.id: opt 
                    for opt in PollOption.objects.filter(poll=poll, pk__in=option_ids_to_fetch)
                }
            
            # OPTIMISATION N+1 : Préparer les ballots en mémoire, puis bulk_create
            ballots_to_create = []
            for vote_data in votes_data:
                option_id = vote_data.get('option_id')
                points = vote_data.get('points', 0)
                if points > 0 and option_id in options_map:
                    option = options_map[option_id]
                    metadata = {"ts": now.isoformat(), "points": points, "intensity": intensity}
                    if not poll.is_anonymous:
                        metadata["user_id"] = request.user.pk
                    ballots_to_create.append(
                        PollBallot(
                            poll=poll,
                            option=option,
                            voter_hash=voter_hash,
                            points=points,
                            weight=weight,
                            saka_spent=saka_spent,
                            metadata=metadata,
                        )
                    )
                    option_ids.append(option_id)
            
            # OPTIMISATION N+1 : Bulk create au lieu de create individuel
            if ballots_to_create:
                PollBallot.objects.bulk_create(ballots_to_create, batch_size=100)
        
        elif poll.voting_method == 'majority':
            # Jugement Majoritaire : classement
            rankings_data = request.data.get("rankings", [])  # [{option_id: 1, ranking: 1}, ...]
            
            # Supprimer les anciens votes
            PollBallot.objects.filter(poll=poll, voter_hash=voter_hash).delete()
            
            # ÉRADICATION N+1 : Récupérer toutes les options en une seule fois
            # Utiliser prefetch_related si poll.options est déjà préchargé
            option_ids_to_fetch = [r.get('option_id') for r in rankings_data]
            if hasattr(poll, '_prefetched_objects_cache') and 'options' in poll._prefetched_objects_cache:
                # Options déjà préchargées, filtrer en Python
                options_map = {
                    opt.id: opt 
                    for opt in poll.options.all() if opt.id in option_ids_to_fetch
                }
            else:
                # Sinon, une seule requête avec filter
                options_map = {
                    opt.id: opt 
                    for opt in PollOption.objects.filter(poll=poll, pk__in=option_ids_to_fetch)
                }
            
            # OPTIMISATION N+1 : Préparer les ballots en mémoire, puis bulk_create
            ballots_to_create = []
            for rank_data in rankings_data:
                option_id = rank_data.get('option_id')
                ranking = rank_data.get('ranking')
                if option_id in options_map:
                    option = options_map[option_id]
                    metadata = {"ts": now.isoformat(), "ranking": ranking}
                    if not poll.is_anonymous:
                        metadata["user_id"] = request.user.pk
                    ballots_to_create.append(
                        PollBallot(
                            poll=poll,
                            option=option,
                            voter_hash=voter_hash,
                            ranking=ranking,
                            metadata=metadata,
                        )
                    )
                    option_ids.append(option_id)
            
            # OPTIMISATION N+1 : Bulk create au lieu de create individuel
            if ballots_to_create:
                PollBallot.objects.bulk_create(ballots_to_create, batch_size=100)
        
        else:
            # Vote Binaire (défaut)
            option_ids = serializer.validated_data["options"]
            PollBallot.objects.filter(poll=poll, voter_hash=voter_hash).exclude(option_id__in=option_ids).delete()

            # ÉRADICATION N+1 : Récupérer toutes les options en une seule fois
            # Utiliser prefetch_related si poll.options est déjà préchargé
            if hasattr(poll, '_prefetched_objects_cache') and 'options' in poll._prefetched_objects_cache:
                # Options déjà préchargées, filtrer en Python
                options_map = {
                    opt.id: opt 
                    for opt in poll.options.all() if opt.id in option_ids
                }
            else:
                # Sinon, une seule requête avec filter
                options_map = {
                    opt.id: opt 
                    for opt in PollOption.objects.filter(poll=poll, pk__in=option_ids)
                }
            
            # OPTIMISATION N+1 : Préparer les ballots en mémoire, puis bulk_create
            # Note: update_or_create n'est pas optimisable en bulk, mais on peut utiliser bulk_create
            # après avoir supprimé les anciens votes
            ballots_to_create = []
            for option_id in option_ids:
                if option_id in options_map:
                    option = options_map[option_id]
                    metadata = {"ts": now.isoformat()}
                    if not poll.is_anonymous:
                        metadata["user_id"] = request.user.pk
                    ballots_to_create.append(
                        PollBallot(
                            poll=poll,
                            option=option,
                            voter_hash=voter_hash,
                            metadata=metadata,
                        )
                    )
            
            # OPTIMISATION N+1 : Bulk create au lieu de update_or_create individuel
            if ballots_to_create:
                PollBallot.objects.bulk_create(ballots_to_create, batch_size=100, ignore_conflicts=True)

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

