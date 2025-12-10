"""
Générateur de passes pour Apple Wallet et Google Wallet
Abstraction générique pour supporter les deux plateformes
"""
import os
import logging
from typing import Literal, Optional
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class WalletConfigMissingError(Exception):
    """Exception levée lorsque la configuration nécessaire pour une plateforme est manquante"""
    pass


def generate_member_pass(user, platform: Literal["apple", "google"]) -> bytes:
    """
    Génère un pass de membre pour Apple Wallet ou Google Wallet.
    
    Args:
        user: Utilisateur Django
        platform: "apple" ou "google"
    
    Returns:
        bytes: Fichier du pass (PKPass pour Apple, JSON pour Google)
    
    Raises:
        WalletConfigMissingError: Si la configuration nécessaire est manquante
    """
    if platform == "apple":
        return _generate_apple_pass(user)
    elif platform == "google":
        return _generate_google_pass(user)
    else:
        raise ValueError(f"Plateforme non supportée: {platform}")


def _generate_apple_pass(user) -> bytes:
    """
    Génère un fichier .pkpass pour Apple Wallet.
    
    Utilise la librairie passbook (ou équivalent) pour créer le pass.
    En mode dev/test, retourne un fichier dummy si la config est manquante.
    """
    # Vérifier la configuration
    cert_path = os.environ.get('APPLE_WALLET_CERT')
    key_path = os.environ.get('APPLE_WALLET_KEY')
    pass_type_id = os.environ.get('APPLE_WALLET_PASS_TYPE_ID')
    team_id = os.environ.get('APPLE_WALLET_TEAM_ID')
    
    if not all([cert_path, key_path, pass_type_id, team_id]):
        if settings.DEBUG:
            logger.warning(
                "Configuration Apple Wallet manquante. "
                "Variables requises: APPLE_WALLET_CERT, APPLE_WALLET_KEY, "
                "APPLE_WALLET_PASS_TYPE_ID, APPLE_WALLET_TEAM_ID"
            )
            # Retourner un fichier dummy en mode dev
            return _generate_dummy_apple_pass(user)
        else:
            raise WalletConfigMissingError(
                "Configuration Apple Wallet non disponible. "
                "Contactez l'administrateur."
            )
    
    try:
        # TODO: Implémenter avec une librairie Python pour Apple Wallet
        # Exemple avec passbook (à installer: pip install passbook)
        # from passbook.models import Pass, Barcode, StoreCard
        
        # wallet = getattr(user, 'wallet', None)
        # balance = wallet.balance if wallet else 0
        
        # pass_obj = Pass(
        #     passTypeIdentifier=pass_type_id,
        #     organizationName="EGOEJO",
        #     teamIdentifier=team_id,
        #     serialNumber=str(user.id),
        #     description="Carte Membre EGOEJO"
        # )
        # pass_obj.storeCard = StoreCard()
        # pass_obj.storeCard.primaryFields.append({
        #     'key': 'name',
        #     'label': 'Membre',
        #     'value': user.username or user.email
        # })
        # pass_obj.storeCard.secondaryFields.append({
        #     'key': 'balance',
        #     'label': 'Solde',
        #     'value': f"{balance} €"
        # })
        # pass_obj.barcode = Barcode(
        #     message=str(user.id),
        #     format='QR',
        #     messageEncoding='iso-8859-1'
        # )
        # 
        # # Signer et créer le .pkpass
        # return pass_obj.create(cert_path, key_path, cert_path, key_path)
        
        # Pour l'instant, retourner un dummy
        logger.warning("Génération Apple Wallet non implémentée, retour d'un dummy")
        return _generate_dummy_apple_pass(user)
        
    except Exception as e:
        logger.error(f"Erreur génération Apple Wallet: {e}")
        raise WalletConfigMissingError(f"Erreur lors de la génération du pass: {str(e)}")


def _generate_google_pass(user) -> bytes:
    """
    Génère un pass JSON pour Google Wallet.
    
    Structure le payload JSON conforme à l'API Google Wallet.
    En mode dev/test, retourne un JSON dummy si la config est manquante.
    """
    service_account = os.environ.get('GOOGLE_WALLET_SERVICE_ACCOUNT')
    issuer_id = os.environ.get('GOOGLE_WALLET_ISSUER_ID')
    class_id = os.environ.get('GOOGLE_WALLET_CLASS_ID')
    
    if not all([service_account, issuer_id, class_id]):
        if settings.DEBUG:
            logger.warning(
                "Configuration Google Wallet manquante. "
                "Variables requises: GOOGLE_WALLET_SERVICE_ACCOUNT, "
                "GOOGLE_WALLET_ISSUER_ID, GOOGLE_WALLET_CLASS_ID"
            )
            # Retourner un JSON dummy en mode dev
            return _generate_dummy_google_pass(user)
        else:
            raise WalletConfigMissingError(
                "Configuration Google Wallet non disponible. "
                "Contactez l'administrateur."
            )
    
    try:
        # TODO: Implémenter avec l'API Google Wallet
        # Exemple de structure JSON pour Google Wallet
        # 
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build
        # 
        # credentials = service_account.Credentials.from_service_account_file(
        #     service_account,
        #     scopes=['https://www.googleapis.com/auth/wallet_object.issuer']
        # )
        # service = build('walletobjects', 'v1', credentials=credentials)
        # 
        # wallet = getattr(user, 'wallet', None)
        # balance = wallet.balance if wallet else 0
        # 
        # loyalty_object = {
        #     'id': f'{issuer_id}.{user.id}',
        #     'classId': class_id,
        #     'state': 'ACTIVE',
        #     'barcode': {
        #         'type': 'QR_CODE',
        #         'value': str(user.id)
        #     },
        #     'accountName': user.username or user.email,
        #     'accountId': str(user.id),
        #     'loyaltyPoints': {
        #         'label': 'Solde',
        #         'balance': {
        #             'string': f"{balance} €"
        #         }
        #     }
        # }
        # 
        # response = service.loyaltyobject().insert(body=loyalty_object).execute()
        # return json.dumps(response).encode('utf-8')
        
        # Pour l'instant, retourner un dummy
        logger.warning("Génération Google Wallet non implémentée, retour d'un dummy")
        return _generate_dummy_google_pass(user)
        
    except Exception as e:
        logger.error(f"Erreur génération Google Wallet: {e}")
        raise WalletConfigMissingError(f"Erreur lors de la génération du pass: {str(e)}")


def _generate_dummy_apple_pass(user) -> bytes:
    """Génère un fichier dummy pour Apple Wallet (mode dev/test)"""
    # Créer un JSON minimal qui simule un PKPass
    import json
    dummy_data = {
        'formatVersion': 1,
        'passTypeIdentifier': 'dummy.pass.egoejo',
        'serialNumber': str(user.id),
        'organizationName': 'EGOEJO',
        'description': 'Carte Membre EGOEJO (Dummy)',
        'storeCard': {
            'primaryFields': [
                {
                    'key': 'name',
                    'label': 'Membre',
                    'value': user.username or user.email
                }
            ]
        }
    }
    return json.dumps(dummy_data).encode('utf-8')


def _generate_dummy_google_pass(user) -> bytes:
    """Génère un JSON dummy pour Google Wallet (mode dev/test)"""
    import json
    wallet = getattr(user, 'wallet', None)
    balance = wallet.balance if wallet else 0
    
    dummy_data = {
        'id': f'dummy.{user.id}',
        'classId': 'dummy.egoejo.member',
        'state': 'ACTIVE',
        'barcode': {
            'type': 'QR_CODE',
            'value': str(user.id)
        },
        'accountName': user.username or user.email,
        'accountId': str(user.id),
        'loyaltyPoints': {
            'label': 'Solde',
            'balance': {
                'string': f"{balance} €"
            }
        },
        'note': 'Pass dummy - Configuration manquante'
    }
    return json.dumps(dummy_data).encode('utf-8')

