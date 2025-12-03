"""
Endpoints REST pour la gestion des projets.
"""

from rest_framework import generics, permissions

from core.models import Projet
from core.serializers import ProjetSerializer


class ProjetListCreate(generics.ListCreateAPIView):
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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

