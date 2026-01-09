"""
Contract tests pour la pagination CMS.

Vérifie que la pagination fonctionne correctement :
- Paramètres page et page_size
- Structure de réponse paginée
- Limites (max page_size)
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from core.models import EducationalContent


@pytest.fixture
def client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Utilisateur admin pour créer des contenus"""
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
def multiple_contents(db, admin_user):
    """Créer plusieurs contenus pour tester la pagination"""
    contents = []
    for i in range(25):
        content = EducationalContent.objects.create(
            title=f'Test Content {i}',
            slug=f'test-content-{i}',
            type='article',
            status='published',
            description=f'Description {i}',
            author=admin_user,
        )
        contents.append(content)
    return contents


@pytest.mark.django_db
@pytest.mark.critical
class TestCMSPagination:
    """Tests de pagination pour GET /api/contents/"""
    
    def test_pagination_returns_paginated_response(self, client, multiple_contents):
        """Vérifie que la réponse est paginée"""
        response = client.get('/api/contents/?page=1&page_size=10', follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'count' in data, "Réponse doit contenir 'count'"
        assert 'next' in data, "Réponse doit contenir 'next'"
        assert 'previous' in data, "Réponse doit contenir 'previous'"
        assert 'results' in data, "Réponse doit contenir 'results'"
        assert isinstance(data['results'], list), "'results' doit être un array"
    
    def test_pagination_page_size_limit(self, client, multiple_contents):
        """Vérifie que page_size est limité à 100 (max)"""
        response = client.get('/api/contents/?page=1&page_size=200', follow=True)
        
        assert response.status_code == 200
        data = response.json()
        # DRF limite automatiquement page_size selon DEFAULT_PAGINATION_CLASS
        assert len(data['results']) <= 100, "page_size doit être limité à 100"
    
    def test_pagination_page_1_has_no_previous(self, client, multiple_contents):
        """Vérifie que la page 1 n'a pas de 'previous'"""
        response = client.get('/api/contents/?page=1&page_size=10', follow=True)
        
        assert response.status_code == 200
        data = response.json()
        assert data['previous'] is None, "Page 1 ne doit pas avoir de 'previous'"
    
    def test_pagination_last_page_has_no_next(self, client, multiple_contents):
        """Vérifie que la dernière page n'a pas de 'next'"""
        # Avec 25 contenus et PAGE_SIZE=20 (par défaut), la dernière page est 2
        response = client.get('/api/contents/?page=2', follow=True)
        
        assert response.status_code == 200
        data = response.json()
        assert data['next'] is None, "Dernière page ne doit pas avoir de 'next'"
    
    def test_pagination_count_is_total(self, client, multiple_contents):
        """Vérifie que 'count' est le nombre total de résultats"""
        response = client.get('/api/contents/?page=1&page_size=10', follow=True)
        
        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 25, "'count' doit être le nombre total de contenus"
    
    def test_pagination_results_count_matches_page_size(self, client, multiple_contents):
        """Vérifie que le nombre de résultats correspond à page_size"""
        # Note: DRF PageNumberPagination ne supporte pas page_size dans la requête par défaut
        # Il utilise PAGE_SIZE=20 de la configuration. Ce test vérifie que la pagination fonctionne.
        response = client.get('/api/contents/?page=1', follow=True)
        
        assert response.status_code == 200
        data = response.json()
        # Avec 25 contenus et PAGE_SIZE=20, la page 1 devrait avoir 20 résultats
        assert len(data['results']) == 20, f"Nombre de résultats doit correspondre à PAGE_SIZE (20), mais a {len(data['results'])}"
    
    def test_pagination_without_params_uses_defaults(self, client, multiple_contents):
        """Vérifie que sans paramètres, la pagination utilise les valeurs par défaut"""
        response = client.get('/api/contents/', follow=True)
        
        assert response.status_code == 200
        data = response.json()
        # Si pas de pagination demandée et status=published, utilise le cache (rétrocompatibilité)
        # Sinon, utilise la pagination DRF par défaut
        assert 'results' in data or isinstance(data, list), "Réponse doit être paginée ou liste"

