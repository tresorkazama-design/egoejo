"""
Endpoints REST pour la gestion des projets.
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from core.models import Projet
from core.serializers import ProjetSerializer


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
        pour éviter les N+1 queries
        """
        queryset = Projet.objects.all().order_by("-created_at")
        
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
        
        return projet

