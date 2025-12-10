"""
Vues API pour l'application Investment (V2.0 dormant).
Protégées par IsInvestmentFeatureEnabled pour bloquer l'accès si feature désactivée.
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from core.permissions import IsInvestmentFeatureEnabled
from .models import ShareholderRegister


class ShareholderRegisterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour le registre des actionnaires.
    En lecture seule (GET uniquement).
    Bloqué si ENABLE_INVESTMENT_FEATURES = False.
    """
    queryset = ShareholderRegister.objects.all()
    serializer_class = None  # À créer si nécessaire
    permission_classes = [IsInvestmentFeatureEnabled, permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrer par projet si fourni.
        """
        queryset = ShareholderRegister.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """
        Liste des actionnaires pour un projet spécifique.
        """
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id requis'}, status=400)
        
        shareholders = ShareholderRegister.objects.filter(project_id=project_id)
        data = [{
            'investor': sh.investor.username,
            'number_of_shares': sh.number_of_shares,
            'amount_invested': str(sh.amount_invested),
            'is_signed': sh.is_signed,
            'created_at': sh.created_at
        } for sh in shareholders]
        
        return Response(data)
