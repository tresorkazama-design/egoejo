"""
Tests de permissions pour les endpoints Finance.

Vérifie que les permissions sont correctement appliquées selon les rôles :
- Utilisateur anonyme → 401 pour tous les endpoints
- Utilisateur authentifié → 200 pour tous les endpoints
- Admin → 200 pour tous les endpoints

Endpoints testés (3) :
1. POST /api/wallet/pockets/transfer/ - IsAuthenticated
2. GET  /api/wallet-pass/apple/ - IsAuthenticated
3. GET  /api/wallet-pass/google/ - IsAuthenticated
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from finance.models import UserWallet, WalletPocket

User = get_user_model()


@pytest.fixture
def client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def regular_user(db):
    """Utilisateur authentifié (non-admin)"""
    return User.objects.create_user(
        username='regular',
        email='regular@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Utilisateur admin (superuser)"""
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123'
    )
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def user_wallet(db, regular_user):
    """Wallet utilisateur avec solde"""
    wallet, _ = UserWallet.objects.get_or_create(
        user=regular_user,
        defaults={'balance': 1000.00}
    )
    return wallet


@pytest.fixture
def wallet_pocket(db, user_wallet):
    """Pocket de test"""
    return WalletPocket.objects.create(
        wallet=user_wallet,
        name='Test Pocket',
        pocket_type='DONATION',
        balance=0.00,
    )


def assert_permission(client, url, method, user, expected_status, data=None):
    """
    Helper pour tester les permissions d'un endpoint.
    
    Args:
        client: APIClient
        url: URL de l'endpoint
        method: 'get', 'post', 'put', 'delete', etc.
        user: User ou None (pour anonyme)
        expected_status: Status HTTP attendu (ou liste de status acceptables)
        data: Données pour POST/PUT (optionnel)
    """
    # Réinitialiser l'authentification du client
    client.force_authenticate(user=None)
    
    if user:
        client.force_authenticate(user=user)
    # Si user est None, on laisse le client non authentifié (pas besoin de force_authenticate)
    
    method_func = getattr(client, method.lower())
    if data:
        response = method_func(url, data, format='json')
    else:
        response = method_func(url)
    
    # DRF peut retourner 401 ou 403 selon le contexte
    # 401 = non authentifié, 403 = authentifié mais sans permissions
    # Pour les utilisateurs anonymes, on accepte les deux codes
    if user is None and expected_status == status.HTTP_401_UNAUTHORIZED:
        expected_status = [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    if isinstance(expected_status, list):
        assert response.status_code in expected_status, (
            f"Expected status in {expected_status}, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    else:
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )


@pytest.mark.django_db
@pytest.mark.critical
class TestPocketTransferPermissions:
    """Tests de permissions pour POST /api/wallet/pockets/transfer/"""
    
    def test_anonymous_cannot_transfer(self, client, wallet_pocket):
        """Un utilisateur anonyme ne peut pas transférer → 401"""
        url = reverse('pocket-transfer')
        data = {
            'pocket_id': wallet_pocket.id,
            'amount': '50.00',
        }
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_authenticated_user_can_transfer(self, client, regular_user, wallet_pocket):
        """Un utilisateur authentifié peut transférer → 200 (ou 400 si solde insuffisant)"""
        url = reverse('pocket-transfer')
        data = {
            'pocket_id': wallet_pocket.id,
            'amount': '50.00',
        }
        # Peut retourner 200 (succès) ou 400 (solde insuffisant/invalide)
        assert_permission(client, url, 'post', regular_user, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST], data=data)
    
    def test_admin_can_transfer(self, client, admin_user, wallet_pocket):
        """Un admin peut transférer → 200 (ou 400 si solde insuffisant)"""
        # Créer un wallet pour l'admin
        UserWallet.objects.get_or_create(
            user=admin_user,
            defaults={'balance': 1000.00}
        )
        url = reverse('pocket-transfer')
        data = {
            'pocket_id': wallet_pocket.id,
            'amount': '50.00',
        }
        # Peut retourner 200 (succès) ou 400 (solde insuffisant/invalide)
        assert_permission(client, url, 'post', admin_user, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST], data=data)


@pytest.mark.django_db
@pytest.mark.critical
class TestWalletPassApplePermissions:
    """Tests de permissions pour GET /api/wallet-pass/apple/"""
    
    def test_anonymous_cannot_get_apple_pass(self, client):
        """Un utilisateur anonyme ne peut pas obtenir le pass Apple → 401"""
        url = reverse('wallet-pass-apple')
        assert_permission(client, url, 'get', None, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_get_apple_pass(self, client, regular_user):
        """Un utilisateur authentifié peut obtenir le pass Apple → 200 (ou 503 si config manquante)"""
        url = reverse('wallet-pass-apple')
        # Peut retourner 200 (succès) ou 503 (config manquante)
        assert_permission(client, url, 'get', regular_user, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
    
    def test_admin_can_get_apple_pass(self, client, admin_user):
        """Un admin peut obtenir le pass Apple → 200 (ou 503 si config manquante)"""
        url = reverse('wallet-pass-apple')
        # Peut retourner 200 (succès) ou 503 (config manquante)
        assert_permission(client, url, 'get', admin_user, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])


@pytest.mark.django_db
@pytest.mark.critical
class TestWalletPassGooglePermissions:
    """Tests de permissions pour GET /api/wallet-pass/google/"""
    
    def test_anonymous_cannot_get_google_pass(self, client):
        """Un utilisateur anonyme ne peut pas obtenir le pass Google → 401"""
        url = reverse('wallet-pass-google')
        assert_permission(client, url, 'get', None, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_get_google_pass(self, client, regular_user):
        """Un utilisateur authentifié peut obtenir le pass Google → 200 (ou 503 si config manquante)"""
        url = reverse('wallet-pass-google')
        # Peut retourner 200 (succès) ou 503 (config manquante)
        assert_permission(client, url, 'get', regular_user, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
    
    def test_admin_can_get_google_pass(self, client, admin_user):
        """Un admin peut obtenir le pass Google → 200 (ou 503 si config manquante)"""
        url = reverse('wallet-pass-google')
        # Peut retourner 200 (succès) ou 503 (config manquante)
        assert_permission(client, url, 'get', admin_user, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])

