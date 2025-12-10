"""
Endpoints API pour visualisation Mycélium Numérique (3D)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)


class MyceliumDataView(APIView):
    """
    Endpoint pour récupérer les données 3D du Mycélium.
    GET /api/mycelium/data/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retourne les coordonnées 3D de tous les projets et contenus avec embeddings.
        """
        try:
            from core.models.projects import Projet
            from core.models.content import EducationalContent
            
            data = {
                'projets': [],
                'contenus': []
            }
            
            # Récupérer les projets avec coordonnées 3D
            projets = Projet.objects.filter(embedding__isnull=False)
            for projet in projets:
                if projet.embedding and isinstance(projet.embedding, dict):
                    coords = projet.embedding.get('coordinates_3d')
                    if coords:
                        data['projets'].append({
                            'id': projet.id,
                            'titre': projet.titre,
                            'description': projet.description[:200] if projet.description else '',
                            'x': coords.get('x', 0),
                            'y': coords.get('y', 0),
                            'z': coords.get('z', 0),
                            'url': f'/projets/{projet.id}'
                        })
            
            # Récupérer les contenus avec coordonnées 3D
            contenus = EducationalContent.objects.filter(
                embedding__isnull=False,
                status='published'
            )
            for contenu in contenus:
                if contenu.embedding and isinstance(contenu.embedding, dict):
                    coords = contenu.embedding.get('coordinates_3d')
                    if coords:
                        data['contenus'].append({
                            'id': contenu.id,
                            'title': contenu.title,
                            'description': contenu.description[:200] if contenu.description else '',
                            'type': contenu.type,
                            'x': coords.get('x', 0),
                            'y': coords.get('y', 0),
                            'z': coords.get('z', 0),
                            'url': f'/contenus/{contenu.slug}'
                        })
            
            return Response(data)
        
        except Exception as exc:
            logger.error(f"Erreur récupération données Mycélium: {exc}")
            return Response({
                'error': 'Erreur lors de la récupération des données'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyceliumReduceView(APIView):
    """
    Endpoint pour lancer la réduction de dimensionnalité (Admin uniquement).
    POST /api/mycelium/reduce/
    """
    from rest_framework.permissions import IsAdminUser
    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        Lance la tâche Celery de réduction de dimensionnalité.
        """
        try:
            from core.tasks_mycelium import reduce_embeddings_to_3d
            
            content_type = request.data.get('content_type', 'both')
            method = request.data.get('method', 'umap')
            
            # Lancer la tâche
            task = reduce_embeddings_to_3d.delay(content_type, method)
            
            return Response({
                'success': True,
                'task_id': task.id,
                'content_type': content_type,
                'method': method
            })
        
        except Exception as exc:
            logger.error(f"Erreur lancement réduction: {exc}")
            return Response({
                'error': 'Erreur lors du lancement de la réduction'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

