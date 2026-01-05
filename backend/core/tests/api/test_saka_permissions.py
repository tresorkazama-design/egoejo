"""
Tests de permissions pour les endpoints SAKA.

Vérifie que les permissions sont correctement appliquées selon les rôles :
- Utilisateur anonyme → 401/403 selon l'endpoint
- Utilisateur authentifié → 200/403 selon l'endpoint
- Admin → 200 pour tous les endpoints admin

Endpoints testés (9) :
1. GET  /api/saka/silo/ - IsAuthenticated
2. GET  /api/saka/compost-preview/ - IsAuthenticated
3. POST /api/saka/compost-trigger/ - IsAdminUser
4. GET  /api/saka/stats/ - IsAdminUser
5. POST /api/saka/compost-run/ - IsAdminUser
6. GET  /api/saka/compost-logs/ - IsAdminUser
7. GET  /api/saka/cycles/ - IsAuthenticated
8. POST /api/saka/redistribute/ - IsAdminUser
9. GET  /api/saka/transactions/ - IsAuthenticated
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

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


def assert_permission(client, url, method, user, expected_status, data=None):
    """
    Helper pour tester les permissions d'un endpoint.
    
    Args:
        client: APIClient
        url: URL de l'endpoint
        method: 'get', 'post', 'put', 'delete', etc.
        user: User ou None (pour anonyme)
        expected_status: Status HTTP attendu
        data: Données pour POST/PUT (optionnel)
    """
    if user:
        client.force_authenticate(user=user)
    else:
        client.force_authenticate(user=None)
    
    method_func = getattr(client, method.lower())
    if data:
        response = method_func(url, data, format='json')
    else:
        response = method_func(url)
    
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.data if hasattr(response, 'data') else response.content}"
    )


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaSiloPermissions:
    """Tests de permissions pour GET /api/saka/silo/"""
    
    def test_anonymous_cannot_access_silo(self, client):
        """Un utilisateur anonyme ne peut pas accéder au Silo → 401 ou 403"""
        url = reverse('saka-silo')
        # DRF peut retourner 401 ou 403 selon la configuration pour IsAuthenticated
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_can_access_silo(self, client, regular_user):
        """Un utilisateur authentifié peut accéder au Silo → 200"""
        url = reverse('saka-silo')
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_admin_can_access_silo(self, client, admin_user):
        """Un admin peut accéder au Silo → 200"""
        url = reverse('saka-silo')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaCompostPreviewPermissions:
    """Tests de permissions pour GET /api/saka/compost-preview/"""
    
    def test_anonymous_cannot_access_compost_preview(self, client):
        """Un utilisateur anonyme ne peut pas accéder au preview → 401 ou 403"""
        url = reverse('saka-compost-preview')
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_can_access_compost_preview(self, client, regular_user):
        """Un utilisateur authentifié peut accéder au preview → 200"""
        url = reverse('saka-compost-preview')
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_admin_can_access_compost_preview(self, client, admin_user):
        """Un admin peut accéder au preview → 200"""
        url = reverse('saka-compost-preview')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaCompostTriggerPermissions:
    """Tests de permissions pour POST /api/saka/compost-trigger/"""
    
    def test_anonymous_cannot_trigger_compost(self, client):
        """Un utilisateur anonyme ne peut pas déclencher le compostage → 401 ou 403"""
        url = reverse('saka-compost-trigger')
        response = client.post(url, {}, format='json')
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_cannot_trigger_compost(self, client, regular_user):
        """Un utilisateur authentifié ne peut pas déclencher le compostage → 403"""
        url = reverse('saka-compost-trigger')
        assert_permission(client, url, 'post', regular_user, status.HTTP_403_FORBIDDEN, data={})
    
    def test_admin_can_trigger_compost(self, client, admin_user, settings):
        """Un admin peut déclencher le compostage → 200 (ou 403 si SAKA désactivé)"""
        url = reverse('saka-compost-trigger')
        client.force_authenticate(user=admin_user)
        response = client.post(url, {'dry_run': True}, format='json')
        # Si SAKA est désactivé, on accepte 403 avec un message explicite
        if response.status_code == status.HTTP_403_FORBIDDEN:
            assert 'compostage' in response.data.get('detail', '').lower() or 'saka' in response.data.get('detail', '').lower() or 'activé' in response.data.get('detail', '').lower()
        else:
            assert response.status_code == status.HTTP_200_OK, (
                f"Expected status 200, got {response.status_code}. "
                f"Response: {response.data if hasattr(response, 'data') else response.content}"
            )


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaStatsPermissions:
    """Tests de permissions pour GET /api/saka/stats/"""
    
    def test_anonymous_cannot_access_stats(self, client):
        """Un utilisateur anonyme ne peut pas accéder aux stats → 401 ou 403"""
        url = reverse('saka-stats')
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_cannot_access_stats(self, client, regular_user):
        """Un utilisateur authentifié ne peut pas accéder aux stats → 403"""
        url = reverse('saka-stats')
        assert_permission(client, url, 'get', regular_user, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_access_stats(self, client, admin_user):
        """Un admin peut accéder aux stats → 200"""
        url = reverse('saka-stats')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaCompostRunPermissions:
    """Tests de permissions pour POST /api/saka/compost-run/"""
    
    def test_anonymous_cannot_run_compost(self, client):
        """Un utilisateur anonyme ne peut pas lancer le compostage → 401 ou 403"""
        url = reverse('saka-compost-run')
        response = client.post(url, {}, format='json')
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_cannot_run_compost(self, client, regular_user):
        """Un utilisateur authentifié ne peut pas lancer le compostage → 403"""
        url = reverse('saka-compost-run')
        assert_permission(client, url, 'post', regular_user, status.HTTP_403_FORBIDDEN, data={})
    
    def test_admin_can_run_compost(self, client, admin_user):
        """Un admin peut lancer le compostage → 200 (ou 400 si SAKA désactivé)"""
        url = reverse('saka-compost-run')
        client.force_authenticate(user=admin_user)
        response = client.post(url, {}, format='json')
        # Si SAKA est désactivé, on accepte 400 avec un message explicite
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            assert 'saka' in response.data.get('reason', '').lower() or 'disabled' in response.data.get('reason', '').lower()
        else:
            assert response.status_code == status.HTTP_200_OK, (
                f"Expected status 200, got {response.status_code}. "
                f"Response: {response.data if hasattr(response, 'data') else response.content}"
            )


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaCompostLogsPermissions:
    """Tests de permissions pour GET /api/saka/compost-logs/"""
    
    def test_anonymous_cannot_access_compost_logs(self, client):
        """Un utilisateur anonyme ne peut pas accéder aux logs → 401 ou 403"""
        url = reverse('saka-compost-logs')
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_cannot_access_compost_logs(self, client, regular_user):
        """Un utilisateur authentifié ne peut pas accéder aux logs → 403"""
        url = reverse('saka-compost-logs')
        assert_permission(client, url, 'get', regular_user, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_access_compost_logs(self, client, admin_user):
        """Un admin peut accéder aux logs → 200"""
        url = reverse('saka-compost-logs')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaCyclesPermissions:
    """Tests de permissions pour GET /api/saka/cycles/"""
    
    def test_anonymous_cannot_access_cycles(self, client):
        """Un utilisateur anonyme ne peut pas accéder aux cycles → 401 ou 403"""
        url = reverse('saka-cycles')
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_can_access_cycles(self, client, regular_user):
        """Un utilisateur authentifié peut accéder aux cycles → 200"""
        url = reverse('saka-cycles')
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_admin_can_access_cycles(self, client, admin_user):
        """Un admin peut accéder aux cycles → 200"""
        url = reverse('saka-cycles')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaRedistributePermissions:
    """Tests de permissions pour POST /api/saka/redistribute/"""
    
    def test_anonymous_cannot_redistribute(self, client):
        """Un utilisateur anonyme ne peut pas redistribuer → 401 ou 403"""
        url = reverse('saka-redistribute')
        response = client.post(url, {}, format='json')
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_cannot_redistribute(self, client, regular_user):
        """Un utilisateur authentifié ne peut pas redistribuer → 403"""
        url = reverse('saka-redistribute')
        assert_permission(client, url, 'post', regular_user, status.HTTP_403_FORBIDDEN, data={})
    
    def test_admin_can_redistribute(self, client, admin_user):
        """Un admin peut redistribuer → 200 (ou 403 si SAKA désactivé)"""
        url = reverse('saka-redistribute')
        client.force_authenticate(user=admin_user)
        response = client.post(url, {}, format='json')
        # Si SAKA est désactivé, on accepte 403 avec un message explicite
        if response.status_code == status.HTTP_403_FORBIDDEN:
            assert 'saka' in str(response.data.get('reason', '')).lower() or 'disabled' in str(response.data.get('reason', '')).lower()
        else:
            assert response.status_code == status.HTTP_200_OK, (
                f"Expected status 200, got {response.status_code}. "
                f"Response: {response.data if hasattr(response, 'data') else response.content}"
            )


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaTransactionsPermissions:
    """Tests de permissions pour GET /api/saka/transactions/"""
    
    def test_anonymous_cannot_access_transactions(self, client):
        """Un utilisateur anonyme ne peut pas accéder aux transactions → 401 ou 403"""
        url = reverse('saka-transactions')
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), (
            f"Expected status 401 or 403, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_authenticated_user_can_access_transactions(self, client, regular_user):
        """Un utilisateur authentifié peut accéder à ses transactions → 200"""
        url = reverse('saka-transactions')
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_admin_can_access_transactions(self, client, admin_user):
        """Un admin peut accéder à ses transactions → 200"""
        url = reverse('saka-transactions')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)

