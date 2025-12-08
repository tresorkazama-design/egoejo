"""
Chiffrement des données sensibles
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    Classe pour chiffrer/déchiffrer les données sensibles
    """
    
    def __init__(self):
        # Générer ou récupérer la clé de chiffrement
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not encryption_key:
            # Générer une clé depuis SECRET_KEY si ENCRYPTION_KEY n'est pas définie
            secret_key = settings.SECRET_KEY.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'egoejo_salt_2024',  # En production, utiliser un salt unique
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret_key))
            self.cipher = Fernet(key)
        else:
            # Utiliser la clé fournie
            self.cipher = Fernet(encryption_key.encode())
    
    def encrypt(self, data: str) -> str:
        """
        Chiffre une chaîne de caractères
        """
        try:
            if not data:
                return data
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erreur lors du chiffrement: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Déchiffre une chaîne de caractères
        """
        try:
            if not encrypted_data:
                return encrypted_data
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            raise


# Instance globale
_encryption_instance = None


def get_encryption():
    """
    Retourne l'instance de chiffrement (singleton)
    """
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = DataEncryption()
    return _encryption_instance


def encrypt_sensitive_data(data: str) -> str:
    """
    Fonction helper pour chiffrer des données sensibles
    """
    return get_encryption().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    Fonction helper pour déchiffrer des données sensibles
    """
    return get_encryption().decrypt(encrypted_data)

