"""
Endpoints API pour la recherche full-text
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from core.models import Projet
from core.serializers import ProjetSerializer


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
            # Recherche avec similarité trigram
            # Nécessite l'extension PostgreSQL: CREATE EXTENSION IF NOT EXISTS pg_trgm;
            projets = Projet.objects.annotate(
                similarity=TrigramSimilarity('titre', query) +
                           TrigramSimilarity('description', query) * 0.5
            ).filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query) |
                Q(similarity__gt=0.1)  # Seuil de similarité minimum
            ).order_by('-similarity', '-created_at').distinct()[:20]
            
            serializer = ProjetSerializer(projets, many=True)
            return Response({
                'results': serializer.data,
                'count': len(serializer.data),
                'query': query
            })
        except Exception as e:
            # Si pg_trgm n'est pas disponible, fallback sur recherche simple
            projets = Projet.objects.filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query)
            ).order_by('-created_at')[:20]
            
            serializer = ProjetSerializer(projets, many=True)
            return Response({
                'results': serializer.data,
                'count': len(serializer.data),
                'query': query,
                'warning': 'Full-text search not available, using simple search'
            })

