"""
Vues pour la gestion des tokens JWT avec rotation
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)


class RefreshTokenView(APIView):
    """
    Endpoint pour rafraîchir un token avec rotation
    Blackliste l'ancien token et crée un nouveau token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Token de rafraîchissement requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Récupérer l'ancien token
            old_token = RefreshToken(refresh_token)
            
            # Récupérer l'utilisateur depuis le token
            user_id = old_token.get('user_id')
            if not user_id:
                return Response(
                    {'error': 'Token invalide : utilisateur introuvable'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Utilisateur introuvable'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Blacklister l'ancien token
            old_token.blacklist()
            
            # Créer un nouveau token pour le même utilisateur
            new_token = RefreshToken.for_user(user)
            
            return Response({
                'access': str(new_token.access_token),
                'refresh': str(new_token),
            })
        except TokenError as e:
            logger.warning(f'Token refresh error: {e}')
            return Response(
                {'error': 'Token invalide ou expiré'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f'Unexpected error during token refresh: {e}')
            return Response(
                {'error': 'Erreur lors du rafraîchissement du token'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

