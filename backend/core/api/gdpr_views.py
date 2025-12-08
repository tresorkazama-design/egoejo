"""
Vues pour la conformité GDPR/RGPD
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Intent
import logging

logger = logging.getLogger(__name__)


class DataExportView(APIView):
    """
    Export des données utilisateur (droit à la portabilité - GDPR Article 20)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Exporte toutes les données de l'utilisateur
        """
        user = request.user
        
        # Collecter les données
        data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'intents': [],
            'metadata': {
                'export_date': timezone.now().isoformat(),
                'format_version': '1.0',
            }
        }
        
        # Récupérer les intentions de l'utilisateur
        intents = Intent.objects.filter(email=user.email)
        for intent in intents:
            data['intents'].append({
                'id': intent.id,
                'name': intent.name,
                'email': intent.email,
                'message': intent.message,
                'created_at': intent.created_at.isoformat() if intent.created_at else None,
            })
        
        return Response(data, status=status.HTTP_200_OK)


class DataDeleteView(APIView):
    """
    Suppression des données utilisateur (droit à l'oubli - GDPR Article 17)
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        """
        Supprime toutes les données de l'utilisateur
        """
        user = request.user
        
        try:
            # Anonymiser les intentions (garder pour statistiques mais anonymiser)
            intents = Intent.objects.filter(email=user.email)
            for intent in intents:
                intent.email = f'deleted_{intent.id}@deleted.local'
                intent.name = 'Utilisateur supprimé'
                intent.message = '[Message supprimé]'
                intent.save()
            
            # Supprimer le compte utilisateur
            user.delete()
            
            logger.info(f'Compte utilisateur {user.id} supprimé conformément au GDPR')
            
            return Response(
                {'message': 'Vos données ont été supprimées avec succès'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f'Erreur lors de la suppression des données: {e}')
            return Response(
                {'error': 'Erreur lors de la suppression des données'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

