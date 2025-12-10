"""
Vues API pour le système financier (Wallet, Pockets, Transactions)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from decimal import Decimal
import json

from .models import WalletPocket
# Import depuis le fichier services.py (le dossier services/ ne doit pas avoir de __init__.py)
# Utiliser un import absolu pour éviter le conflit avec le dossier services/
from finance.services import transfer_to_pocket, InsufficientBalanceError
from .wallet_services import generate_member_pass, WalletConfigMissingError
from django.core.exceptions import ValidationError


class PocketTransferView(APIView):
    """
    Endpoint pour transférer des fonds du wallet principal vers une pocket.
    POST /api/wallet/pockets/transfer/
    
    Body JSON:
    {
        "pocket_id": int,
        "amount": "string"  # Decimal en string (ex: "100.00")
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
            
            pocket_id = data.get('pocket_id')
            amount_str = data.get('amount')
            
            if not pocket_id:
                return Response(
                    {'error': 'pocket_id est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not amount_str:
                return Response(
                    {'error': 'amount est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir en Decimal
            try:
                amount = Decimal(str(amount_str))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'amount doit être un nombre valide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Effectuer le transfert
            transaction = transfer_to_pocket(request.user, pocket_id, amount)
            
            return Response({
                'success': True,
                'transaction_id': transaction.id,
                'amount': str(transaction.amount),
                'message': 'Transfert effectué avec succès'
            }, status=status.HTTP_200_OK)
            
        except InsufficientBalanceError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du transfert: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletPassAppleView(APIView):
    """
    Endpoint pour télécharger le pass Apple Wallet.
    GET /api/wallet-pass/apple/
    
    Retourne le fichier .pkpass pour ajouter à Apple Wallet.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            pass_data = generate_member_pass(request.user, "apple")
            
            response = Response(pass_data, content_type='application/vnd.apple.pkpass')
            response['Content-Disposition'] = f'attachment; filename="egoejo-member-{request.user.id}.pkpass"'
            return response
            
        except WalletConfigMissingError as e:
            return Response(
                {
                    'error': str(e),
                    'message': 'Apple Wallet n\'est pas encore disponible sur cette plateforme.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du pass: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletPassGoogleView(APIView):
    """
    Endpoint pour télécharger le pass Google Wallet.
    GET /api/wallet-pass/google/
    
    Retourne le JSON du pass pour Google Wallet.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            pass_data = generate_member_pass(request.user, "google")
            
            response = Response(pass_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="egoejo-member-{request.user.id}.json"'
            return response
            
        except WalletConfigMissingError as e:
            return Response(
                {
                    'error': str(e),
                    'message': 'Google Wallet n\'est pas encore disponible sur cette plateforme.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du pass: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

