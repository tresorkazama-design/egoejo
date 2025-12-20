"""
Endpoints API pour la recherche full-text
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.db.utils import ProgrammingError, OperationalError
import logging

from core.models import Projet
from core.serializers import ProjetSerializer

logger = logging.getLogger(__name__)

# PROTECTION OOM : Limite stricte sur les résultats de recherche
MAX_SEARCH_RESULTS = 100


class ProjetSearchView(APIView):
    """
    Endpoint pour la recherche full-text de projets
    GET /api/projets/search/?q=query
    """
    permission_classes = []  # Public

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if len(query) < 2:
            return Response(
                {'error': 'Query must be at least 2 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # PROTECTION OOM : Appliquer la limite AVANT distinct() pour éviter de charger tout en mémoire
            # La limite doit être appliquée directement sur le QuerySet avant toute évaluation
            # Nécessite l'extension PostgreSQL: CREATE EXTENSION IF NOT EXISTS pg_trgm;
            projets_qs = Projet.objects.annotate(
                similarity=TrigramSimilarity('titre', query) +
                           TrigramSimilarity('description', query) * 0.5
            ).filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query) |
                Q(similarity__gt=0.1)  # Seuil de similarité minimum
            ).order_by('-similarity', '-created_at')
            
            # PROTECTION OOM : Appliquer distinct() puis LIMIT directement en SQL
            # Cela génère SELECT DISTINCT ... LIMIT 100 en SQL, pas en Python
            projets = projets_qs.distinct()[:MAX_SEARCH_RESULTS]
            
            serializer = ProjetSerializer(projets, many=True)
            return Response({
                'results': serializer.data,
                'count': len(serializer.data),
                'query': query,
                'max_results': MAX_SEARCH_RESULTS
            })
        except (ProgrammingError, OperationalError) as e:
            # Extension pg_trgm non disponible ou erreur DB - fallback sur recherche simple
            logger.warning(
                f"Extension pg_trgm non disponible ou erreur DB - recherche simple utilisée pour query '{query}': {e}"
            )
            # PROTECTION OOM : Appliquer la limite directement en SQL
            projets = Projet.objects.filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query)
            ).order_by('-created_at')[:MAX_SEARCH_RESULTS]
            
            serializer = ProjetSerializer(projets, many=True)
            return Response({
                'results': serializer.data,
                'count': len(serializer.data),
                'query': query,
                'max_results': MAX_SEARCH_RESULTS,
                'warning': 'Full-text search not available, using simple search'
            })
        except Exception as e:
            # Erreur inattendue - ON LOG CRITIQUE ET ON CONTINUE
            logger.critical(
                f"Erreur critique lors de la recherche pour query '{query}': {e}",
                exc_info=True
            )
            # Fallback sur recherche simple pour ne pas bloquer l'utilisateur
            # PROTECTION OOM : Appliquer la limite directement en SQL
            projets = Projet.objects.filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query)
            ).order_by('-created_at')[:MAX_SEARCH_RESULTS]
            
            serializer = ProjetSerializer(projets, many=True)
            return Response({
                'results': serializer.data,
                'count': len(serializer.data),
                'query': query,
                'max_results': MAX_SEARCH_RESULTS,
                'warning': 'Full-text search not available, using simple search'
            })

