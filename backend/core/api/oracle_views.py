"""
Endpoints API pour les Oracles d'Impact
Permet de récupérer les données des oracles actifs pour un projet
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import logging

from core.models.projects import Projet
from core.services.oracle_manager import OracleManager

logger = logging.getLogger(__name__)


class ProjectOraclesView(APIView):
    """
    Endpoint pour récupérer les données des oracles d'impact d'un projet.
    GET /api/projets/<id>/oracles/
    """
    permission_classes = [AllowAny]  # Public (données d'impact)

    def get(self, request, pk):
        """
        Retourne les données de tous les oracles actifs pour un projet.
        """
        project = get_object_or_404(Projet, pk=pk)
        
        # Récupérer les données des oracles
        try:
            oracle_data = OracleManager.get_oracle_data(project, force_refresh=False)
            
            return Response({
                'project_id': project.id,
                'project_title': project.titre,
                'active_oracles': project.active_oracles or [],
                'oracles': oracle_data.get('oracles', {}),
                'aggregated_metrics': oracle_data.get('aggregated_metrics', {}),
                'metadata': oracle_data.get('metadata', {}),
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données oracle pour le projet {project.id}: {e}", exc_info=True)
            return Response({
                'error': 'Erreur lors de la récupération des données oracle',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableOraclesView(APIView):
    """
    Endpoint pour lister tous les oracles d'impact disponibles.
    GET /api/oracles/available/
    """
    permission_classes = [AllowAny]  # Public

    def get(self, request):
        """
        Retourne la liste de tous les oracles disponibles avec leurs métadonnées.
        """
        try:
            oracles = OracleManager.get_available_oracles()
            
            return Response({
                'oracles': oracles,
                'count': len(oracles),
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des oracles: {e}", exc_info=True)
            return Response({
                'error': 'Erreur lors de la récupération de la liste des oracles',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

