"""
Vues API pour le système financier (Wallet, Pockets, Transactions)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.decorators import permission_classes
from decimal import Decimal
import json
import logging

from .models import WalletPocket
# Import depuis le fichier services.py (le dossier services/ ne doit pas avoir de __init__.py)
# Utiliser un import absolu pour éviter le conflit avec le dossier services/
from finance.services import transfer_to_pocket, InsufficientBalanceError
from .wallet_services import generate_member_pass, WalletConfigMissingError
from finance.ledger_services.ledger import process_stripe_payment_webhook
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


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


@permission_classes([AllowAny])  # Stripe webhook n'utilise pas l'authentification standard
class StripeWebhookView(APIView):
    """
    Endpoint pour recevoir les webhooks Stripe.
    POST /api/finance/stripe/webhook/
    
    Gère les événements Stripe, notamment payment_intent.succeeded pour
    allouer les fonds aux Ledgers avec répartition proportionnelle des frais.
    
    Sécurité :
    - Vérification de la signature Stripe (à implémenter si nécessaire)
    - Idempotence via idempotency_key
    """
    
    def post(self, request):
        """
        Traite un webhook Stripe.
        
        Body JSON (événement Stripe):
        {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_xxx",
                    "amount": 10500,  # en centimes
                    "metadata": {
                        "donation_amount": "100.00",
                        "tip_amount": "5.00",
                        "user_id": "123",
                        "project_id": "456"
                    },
                    "charges": {
                        "data": [{
                            "balance_transaction": {
                                "fee": 183  # en centimes
                            }
                        }]
                    }
                }
            }
        }
        """
        try:
            event_data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
            event_type = event_data.get('type')
            
            if not event_type:
                return Response(
                    {'error': 'Type d\'événement manquant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Traiter uniquement payment_intent.succeeded
            if event_type == 'payment_intent.succeeded':
                return self._handle_payment_intent_succeeded(event_data)
            else:
                # Autres événements : on les ignore pour l'instant
                logger.info(f"Événement Stripe ignoré: {event_type}")
                return Response({'status': 'ignored'}, status=status.HTTP_200_OK)
                
        except json.JSONDecodeError:
            return Response(
                {'error': 'JSON invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement du webhook Stripe: {e}", exc_info=True)
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_payment_intent_succeeded(self, event_data):
        """
        Traite un événement payment_intent.succeeded.
        """
        try:
            payment_intent = event_data.get('data', {}).get('object', {})
            metadata = payment_intent.get('metadata', {})
            
            # Récupérer user_id et project_id depuis metadata
            user_id = metadata.get('user_id')
            project_id = metadata.get('project_id')
            
            if not user_id:
                logger.error("user_id manquant dans metadata du payment_intent")
                return Response(
                    {'error': 'user_id manquant dans metadata'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(id=int(user_id))
            except (User.DoesNotExist, ValueError):
                logger.error(f"Utilisateur introuvable: user_id={user_id}")
                return Response(
                    {'error': f'Utilisateur introuvable: {user_id}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupérer le projet si project_id est fourni
            project = None
            if project_id:
                try:
                    from core.models import Projet
                    project = Projet.objects.get(id=int(project_id))
                except (Projet.DoesNotExist, ValueError):
                    logger.warning(f"Projet introuvable: project_id={project_id}, continuation sans projet")
            
            # Traiter le webhook avec process_stripe_payment_webhook
            result = process_stripe_payment_webhook(
                webhook_event_data=event_data,
                user=user,
                project=project
            )
            
            return Response({
                'status': 'success',
                'donation': {
                    'amount_gross': str(result['donation']['amount_gross']) if result['donation'] else None,
                    'stripe_fee': str(result['donation']['stripe_fee']) if result['donation'] else None,
                    'amount_net': str(result['donation']['amount_net']) if result['donation'] else None,
                    'transaction_id': result['donation']['transaction'].id if result['donation'] and result['donation']['transaction'] else None,
                } if result.get('donation') else None,
                'tip': {
                    'amount_gross': str(result['tip']['amount_gross']) if result['tip'] else None,
                    'stripe_fee': str(result['tip']['stripe_fee']) if result['tip'] else None,
                    'amount_net': str(result['tip']['amount_net']) if result['tip'] else None,
                    'transaction_id': result['tip']['transaction'].id if result['tip'] and result['tip']['transaction'] else None,
                } if result.get('tip') else None,
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.error(f"Erreur de validation lors du traitement du webhook: {e}")
            return Response(
                {'error': f'Erreur de validation: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement du payment_intent.succeeded: {e}", exc_info=True)
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

