"""
Endpoints API pour le Concierge Support
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.exceptions import PermissionDenied

from core.models.chat import ChatThread
from core.services.concierge import is_user_concierge_eligible, get_or_create_concierge_thread
from core.serializers.chat import ChatThreadSerializer


class ConciergeThreadView(APIView):
    """
    Endpoint pour récupérer ou créer le thread Concierge pour l'utilisateur courant.
    GET /api/support/concierge/
    
    Retourne le thread SUPPORT_CONCIERGE de l'utilisateur s'il est éligible.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Vérifier l'éligibilité
        if not is_user_concierge_eligible(user):
            return Response(
                {
                    'eligible': False,
                    'message': 'Vous n\'êtes pas éligible au Concierge Support. '
                               'Conditions : Premium, ou 500€+ de dons, ou 1000€+ d\'investissements.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer ou créer le thread
        try:
            thread, created = get_or_create_concierge_thread(user)
            serializer = ChatThreadSerializer(thread, context={'request': request})
            
            return Response({
                'eligible': True,
                'thread': serializer.data,
                'created': created
            }, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response(
                {'eligible': False, 'message': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class ConciergeEligibilityView(APIView):
    """
    Endpoint pour vérifier l'éligibilité au Concierge Support.
    GET /api/support/concierge/eligibility/
    
    Retourne si l'utilisateur est éligible sans créer de thread.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        eligible = is_user_concierge_eligible(user)
        
        return Response({
            'eligible': eligible
        }, status=status.HTTP_200_OK)


class SupportContactView(APIView):
    """
    Endpoint pour le formulaire de contact (fallback si non éligible au Concierge).
    POST /api/support/contact/
    
    Body JSON:
    {
        "name": "string",
        "email": "string",
        "message": "string"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            name = data.get('name', '')
            email = data.get('email', '')
            message = data.get('message', '')
            
            if not message:
                return Response(
                    {'error': 'Le message est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # TODO: Envoyer un email ou créer un ticket de support
            # Pour l'instant, on log juste
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Contact support: {name} ({email}) - {message}')
            
            return Response({
                'success': True,
                'message': 'Votre message a été envoyé. Nous vous répondrons sous 24h.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de l\'envoi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

