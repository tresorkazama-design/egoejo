"""
Endpoints REST pour la gestion des projets.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.shortcuts import get_object_or_404

from core.models import Projet
from core.serializers import ProjetSerializer
from core.services.saka import spend_saka
from core.services.impact_4p import update_project_4p


class ProjetRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint pour récupérer, mettre à jour ou supprimer un projet individuel.
    GET /api/projets/<id>/
    """
    queryset = Projet.objects.all()
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProjetListCreate(generics.ListCreateAPIView):
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @method_decorator(cache_page(300))  # Cache 5 minutes pour GET
    def get(self, request, *args, **kwargs):
        cache_key = 'projets_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            # Récupérer les données depuis la DB
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            cached_data = serializer.data
            # Mettre en cache pour 5 minutes
            cache.set(cache_key, cached_data, 300)
        
        return Response(cached_data)
    
    def get_queryset(self):
        """
        Optimisation des requêtes avec select_related et prefetch_related
        pour éviter les N+1 queries.
        Phase 2 : Trier par saka_score si SAKA_PROJECT_BOOST_ENABLED est activé.
        """
        queryset = Projet.objects.all()
        
        # Phase 2 : Trier par saka_score si activé
        if getattr(settings, "ENABLE_SAKA", False) and getattr(settings, "SAKA_PROJECT_BOOST_ENABLED", False):
            queryset = queryset.order_by("-saka_score", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")
        
        # Optimiser les relations ForeignKey
        queryset = queryset.select_related(
            # Ajouter les relations ForeignKey si elles existent
            # 'auteur',  # Exemple si Projet a une ForeignKey vers User
        )
        
        # Optimiser les relations ManyToMany et Reverse ForeignKey
        queryset = queryset.prefetch_related(
            # Ajouter les relations ManyToMany si elles existent
            # 'tags',  # Exemple si Projet a une ManyToMany vers Tag
            # 'images',  # Exemple si Projet a une relation vers Image
        )
        
        return queryset
    
    def perform_create(self, serializer):
        # Créer le projet
        projet = serializer.save()
        
        # Scanner l'image si uploadée (tâche asynchrone)
        if projet.image:
            try:
                from core.tasks_security import scan_file_antivirus
                scan_file_antivirus.delay(projet.image.name)
            except Exception:
                # Ignorer si Celery non disponible
                pass
        
        # Générer embedding en arrière-plan (tâche asynchrone)
        try:
            from core.tasks_embeddings import generate_embedding_task
            # Utiliser Sentence Transformers par défaut (gratuit)
            generate_embedding_task.delay('sentence-transformers', projet.id, 'projet')
        except Exception:
            # Ignorer si Celery non disponible
            pass
        
        # Invalider le cache
        cache.delete('projets_list')
        
        # Mettre à jour les scores 4P après création du projet
        try:
            update_project_4p(projet)
        except Exception:
            # Ne pas faire échouer la création si le calcul 4P échoue
            pass
        
        return projet


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def boost_project(request, pk):
    """
    Sorgho-boosting : Nourrir un projet avec des grains SAKA (Phase 2).
    POST /api/projets/<id>/boost/
    
    SÉCURISÉ CONTRE LES RACE CONDITIONS :
    - Transaction atomique globale
    - Verrouillage du wallet ET du projet avec select_for_update()
    - Utilise SakaProjectSupport pour tracker les supporters uniques
    
    Body JSON (optionnel):
    {
        "amount": 10  // Montant SAKA à dépenser (défaut: SAKA_PROJECT_BOOST_COST)
    }
    """
    from django.db import transaction
    from django.db.models import F
    
    # Vérifier que SAKA est activé
    if not getattr(settings, "ENABLE_SAKA", False):
        return Response(
            {"detail": "Le protocole SAKA n'est pas activé."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not getattr(settings, "SAKA_PROJECT_BOOST_ENABLED", False):
        return Response(
            {"detail": "Le Sorgho-boosting n'est pas activé."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Déterminer le coût SAKA
    cost = int(request.data.get("amount", getattr(settings, "SAKA_PROJECT_BOOST_COST", 10)))
    
    if cost <= 0:
        return Response(
            {"detail": "Le montant SAKA doit être strictement positif."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Transaction atomique globale pour garantir la cohérence
    with transaction.atomic():
        # Verrouiller le projet avec select_for_update()
        project = get_object_or_404(
            Projet.objects.select_for_update(),
            pk=pk
        )
        
        # Tenter de dépenser les SAKA (déjà sécurisé avec transaction atomique)
        if not spend_saka(
            request.user,
            cost,
            reason="project_boost",
            metadata={"project_id": project.id}
        ):
            return Response(
                {"detail": "Solde SAKA insuffisant."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le score du projet avec F() expression
        Projet.objects.filter(id=project.id).update(
            saka_score=F('saka_score') + cost
        )
        
        # Gérer le compteur de supporters via SakaProjectSupport
        from core.models.saka import SakaProjectSupport
        support, created = SakaProjectSupport.objects.get_or_create(
            user=request.user,
            project=project,
            defaults={'total_saka_spent': cost}
        )
        
        if not created:
            # Mettre à jour le total dépensé
            SakaProjectSupport.objects.filter(id=support.id).update(
                total_saka_spent=F('total_saka_spent') + cost
            )
        else:
            # Nouveau supporter : incrémenter le compteur
            Projet.objects.filter(id=project.id).update(
                saka_supporters_count=F('saka_supporters_count') + 1
            )
        
        # Recharger le projet pour obtenir les valeurs à jour
        project.refresh_from_db()
    
    # Mettre à jour les scores 4P après le boost SAKA
    # (en dehors de la transaction pour éviter de bloquer trop longtemps)
    try:
        update_project_4p(project)
    except Exception:
        # Ne pas faire échouer le boost si le calcul 4P échoue
        pass
    
    # Invalider le cache
    cache.delete('projets_list')
    
    return Response({
        "ok": True,
        "message": f"Projet '{project.titre}' boosté avec {cost} grains SAKA.",
        "saka_spent": cost,
        "saka_score": project.saka_score,
        "saka_supporters_count": project.saka_supporters_count,
    }, status=status.HTTP_200_OK)

