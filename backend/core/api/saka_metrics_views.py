"""
API endpoints pour les métriques du protocole SAKA
Permet de monitorer l'exécution du compostage et de la redistribution
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from core.services.saka_metrics import (
    get_compost_metrics,
    get_redistribution_metrics,
    get_silo_metrics,
    get_global_saka_metrics,
    get_cycle_metrics,
)


class SakaCompostMetricsView(APIView):
    """
    Endpoint pour récupérer les métriques de compostage
    Admin uniquement
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retourne les métriques de compostage sur les 30 derniers jours
        """
        days = int(request.query_params.get('days', 30))
        metrics = get_compost_metrics(days=days)
        return Response(metrics, status=status.HTTP_200_OK)


class SakaRedistributionMetricsView(APIView):
    """
    Endpoint pour récupérer les métriques de redistribution
    Admin uniquement
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retourne les métriques de redistribution sur les 90 derniers jours
        """
        days = int(request.query_params.get('days', 90))
        metrics = get_redistribution_metrics(days=days)
        return Response(metrics, status=status.HTTP_200_OK)


class SakaSiloMetricsView(APIView):
    """
    Endpoint pour récupérer les métriques du Silo Commun
    Admin uniquement
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retourne les métriques du Silo Commun
        """
        metrics = get_silo_metrics()
        return Response(metrics, status=status.HTTP_200_OK)


class SakaGlobalMetricsView(APIView):
    """
    Endpoint pour récupérer les métriques globales du protocole SAKA
    Admin uniquement
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retourne les métriques globales du protocole SAKA
        """
        metrics = get_global_saka_metrics()
        return Response(metrics, status=status.HTTP_200_OK)


class SakaCycleMetricsView(APIView):
    """
    Endpoint pour récupérer les métriques des cycles SAKA
    Admin uniquement
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retourne les métriques des cycles SAKA
        """
        metrics = get_cycle_metrics()
        return Response(metrics, status=status.HTTP_200_OK)


class SakaAllMetricsView(APIView):
    """
    Endpoint pour récupérer toutes les métriques SAKA en une seule requête
    Admin uniquement
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retourne toutes les métriques SAKA
        """
        return Response({
            'compost': get_compost_metrics(days=30),
            'redistribution': get_redistribution_metrics(days=90),
            'silo': get_silo_metrics(),
            'global': get_global_saka_metrics(),
            'cycles': get_cycle_metrics(),
        }, status=status.HTTP_200_OK)

