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
from finance.ledger_services.helloasso_ledger import process_helloasso_payment_webhook
from finance.stripe_utils import verify_stripe_signature, ensure_test_mode
from finance.helloasso_client import HelloAssoClient
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
    - Vérification de la signature Stripe (STRIPE_WEBHOOK_SECRET)
    - Idempotence via idempotency_key (event.id + payment_intent.id)
    - Mode test strict : refuse clés live si STRIPE_TEST_MODE_ONLY=True
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
        # Vérifier le mode test strict (refuser clés live en CI)
        try:
            ensure_test_mode()
        except Exception as e:
            logger.error(f"Erreur mode test strict: {e}")
            return Response(
                {'error': 'Configuration Stripe invalide (mode test requis)'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Vérifier la signature Stripe
        signature_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        payload = request.body if isinstance(request.body, bytes) else request.body.encode('utf-8')
        
        if not verify_stripe_signature(payload, signature_header):
            logger.warning("Signature Stripe invalide ou manquante")
            return Response(
                {'error': 'Signature Stripe invalide'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            event_data = json.loads(payload.decode('utf-8')) if isinstance(payload, bytes) else json.loads(payload)
            event_type = event_data.get('type')
            event_id = event_data.get('id')  # Pour idempotence
            
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


@permission_classes([IsAuthenticated])
class HelloAssoCheckoutView(APIView):
    """
    Endpoint pour créer un formulaire de paiement HelloAsso.
    POST /api/payments/helloasso/start/
    
    Mode simulé uniquement (pas de réseau externe en CI).
    """
    
    def post(self, request):
        """
        Crée un formulaire de paiement HelloAsso.
        
        Body JSON:
        {
            "amount": "100.00",  # Decimal en string
            "project_id": 123,  # Optionnel
            "metadata": {}  # Optionnel
        }
        """
        try:
            data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
            
            amount_str = data.get('amount')
            project_id = data.get('project_id')
            metadata = data.get('metadata', {})
            
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
            
            if amount <= Decimal('0'):
                return Response(
                    {'error': 'amount doit être strictement positif'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupérer le projet si project_id est fourni
            project = None
            if project_id:
                try:
                    from core.models import Projet
                    project = Projet.objects.get(id=int(project_id))
                except (Projet.DoesNotExist, ValueError):
                    return Response(
                        {'error': f'Projet introuvable: {project_id}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Créer le client HelloAsso (mode simulé)
            client = HelloAssoClient()
            
            # Créer le formulaire de paiement
            payment_form = client.create_payment_form(
                amount=float(amount),
                user_id=request.user.id,
                project_id=project.id if project else None,
                metadata={
                    **metadata,
                    'user_id': str(request.user.id),
                    'project_id': str(project.id) if project else None,
                    'donation_amount': str(amount),
                    'tip_amount': '0.00'
                }
            )
            
            return Response({
                'success': True,
                'payment_form_url': payment_form['payment_form_url'],
                'payment_form_id': payment_form['payment_form_id'],
                'expires_at': payment_form['expires_at']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du formulaire HelloAsso: {e}", exc_info=True)
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@permission_classes([AllowAny])  # HelloAsso webhook n'utilise pas l'authentification standard
class HelloAssoWebhookView(APIView):
    """
    Endpoint pour recevoir les webhooks HelloAsso.
    POST /api/payments/helloasso/webhook/
    
    Mode simulé uniquement (pas de réseau externe en CI).
    
    Sécurité :
    - Vérification de la signature HelloAsso (X-HelloAsso-Signature)
    - Idempotence via event.id + payment.id
    """
    
    def post(self, request):
        """
        Traite un webhook HelloAsso.
        
        Body JSON (événement HelloAsso):
        {
            "eventType": "Payment",
            "eventId": "evt_123",
            "data": {
                "payment": {
                    "id": "payment_123",
                    "amount": 10000,  # en centimes
                    "fee": 80,  # en centimes (optionnel)
                    "metadata": {
                        "user_id": "123",
                        "project_id": "456",
                        "donation_amount": "100.00",
                        "tip_amount": "0.00"
                    }
                }
            }
        }
        """
        # Vérifier la signature HelloAsso
        signature_header = request.META.get('HTTP_X_HELLOASSO_SIGNATURE', '')
        payload = request.body if isinstance(request.body, bytes) else request.body.encode('utf-8')
        
        client = HelloAssoClient()
        if not client.verify_webhook_signature(payload, signature_header):
            logger.warning("Signature HelloAsso invalide ou manquante")
            return Response(
                {'error': 'Signature HelloAsso invalide'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            event_data = json.loads(payload.decode('utf-8')) if isinstance(payload, bytes) else json.loads(payload)
            event_type = event_data.get('eventType')
            event_id = event_data.get('eventId')  # Pour idempotence
            
            if not event_type:
                return Response(
                    {'error': 'Type d\'événement manquant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Traiter uniquement Payment
            if event_type == 'Payment':
                return self._handle_payment_event(event_data, event_id)
            else:
                # Autres événements : on les ignore pour l'instant
                logger.info(f"Événement HelloAsso ignoré: {event_type}")
                return Response({'status': 'ignored'}, status=status.HTTP_200_OK)
                
        except json.JSONDecodeError:
            return Response(
                {'error': 'JSON invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement du webhook HelloAsso: {e}", exc_info=True)
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_payment_event(self, event_data, event_id):
        """
        Traite un événement Payment HelloAsso.
        """
        try:
            payment = event_data.get('data', {}).get('payment', {})
            metadata = payment.get('metadata', {})
            
            # Récupérer user_id depuis metadata
            user_id = metadata.get('user_id')
            project_id = metadata.get('project_id')
            
            if not user_id:
                logger.error("user_id manquant dans metadata du payment HelloAsso")
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
            
            # Vérifier l'idempotence via event.id
            payment_id = payment.get('id', '')
            if event_id and payment_id:
                # Vérifier si cet événement a déjà été traité
                from finance.models import WalletTransaction
                import uuid as uuid_module
                namespace = uuid_module.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                idempotency_key = uuid_module.uuid5(namespace, f"helloasso_{event_id}_{payment_id}")
                
                if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
                    logger.warning(f"Événement HelloAsso déjà traité (idempotence): event_id={event_id}, payment_id={payment_id}")
                    return Response({
                        'status': 'success',
                        'message': 'Événement déjà traité (idempotence)'
                    }, status=status.HTTP_200_OK)
            
            # Traiter le webhook avec process_helloasso_payment_webhook
            result = process_helloasso_payment_webhook(
                webhook_event_data=event_data,
                user=user,
                project=project
            )
            
            return Response({
                'status': 'success',
                'donation': {
                    'amount_gross': str(result['donation']['amount_gross']) if result['donation'] else None,
                    'helloasso_fee': str(result['donation']['stripe_fee']) if result['donation'] else None,  # Utilise stripe_fee pour HelloAsso
                    'amount_net': str(result['donation']['amount_net']) if result['donation'] else None,
                    'transaction_id': result['donation']['transaction'].id if result['donation'] and result['donation']['transaction'] else None,
                } if result.get('donation') else None,
                'tip': {
                    'amount_gross': str(result['tip']['amount_gross']) if result['tip'] else None,
                    'helloasso_fee': str(result['tip']['stripe_fee']) if result['tip'] else None,
                    'amount_net': str(result['tip']['amount_net']) if result['tip'] else None,
                    'transaction_id': result['tip']['transaction'].id if result['tip'] and result['tip']['transaction'] else None,
                } if result.get('tip') else None,
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.error(f"Erreur de validation lors du traitement du webhook HelloAsso: {e}")
            return Response(
                {'error': f'Erreur de validation: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement du payment HelloAsso: {e}", exc_info=True)
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

