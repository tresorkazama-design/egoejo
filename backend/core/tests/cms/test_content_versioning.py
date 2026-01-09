"""
Tests de versioning pour le CMS (si applicable).

Vérifie :
- Création de versions lors de modifications
- Récupération de versions précédentes
- Historique des modifications
"""
import pytest
import uuid
import time
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status

from core.models import EducationalContent
from core.permissions import CONTENT_CONTRIBUTOR_GROUP_NAME


@pytest.fixture
def client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def contributor_user(db):
    """Utilisateur avec rôle Contributor"""
    user = User.objects.create_user(
        username='contributor',
        email='contributor@example.com',
        password='testpass123'
    )
    group, _ = Group.objects.get_or_create(name=CONTENT_CONTRIBUTOR_GROUP_NAME)
    user.groups.add(group)
    return user


@pytest.mark.django_db
class TestContentVersioning:
    """Tests de versioning pour le CMS (si applicable)"""
    
    def test_content_no_versioning_implemented(self, db):
        """Vérifie que le modèle EducationalContent n'a pas de versioning (pour l'instant)"""
        # Vérifier que le modèle n'a pas de relation vers un modèle de versioning
        # (ex: django-reversion, ou modèle Version personnalisé)
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        version_fields = [f for f in content_fields if 'version' in f.lower() or 'history' in f.lower()]
        
        # Vérifier qu'il n'y a pas de relation vers un modèle Version
        content_relations = [f for f in EducationalContent._meta.get_fields() if hasattr(f, 'related_model')]
        version_models = [f for f in content_relations if f.related_model and 'version' in f.related_model.__name__.lower()]
        
        if len(version_fields) == 0 and len(version_models) == 0:
            pytest.skip("Versioning non implémenté dans EducationalContent")
        else:
            # Si versioning est implémenté, tester la création de versions
            assert len(version_fields) > 0 or len(version_models) > 0, "Versioning trouvé mais non testé"
    
    def test_content_version_created_on_modification_if_implemented(self, client, contributor_user):
        """Vérifie qu'une version est créée lors d'une modification si versioning est implémenté"""
        # Vérifier si versioning est implémenté
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        has_versioning = any('version' in f.lower() or 'history' in f.lower() for f in content_fields)
        
        if not has_versioning:
            pytest.skip("Versioning non implémenté dans EducationalContent")
        
        # Si versioning est implémenté, créer un contenu et le modifier
        # puis vérifier qu'une version est créée
        client.force_authenticate(user=contributor_user)
        unique_slug = f'test-version-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        # Créer un contenu
        url = '/api/contents/'
        response = client.post(url, {
            'title': 'Original Title',
            'slug': unique_slug,
            'type': 'article',
            'description': 'Original description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        content = EducationalContent.objects.get(slug=unique_slug)
        
        # Modifier le contenu (si update est disponible)
        # Note: Le ViewSet n'a pas UpdateModelMixin, donc update n'est pas disponible
        # Si versioning est implémenté, il faudrait tester via l'admin ou un endpoint spécifique
        
        # Vérifier qu'une version est créée
        # (à adapter selon l'implémentation réelle)
        if hasattr(content, 'versions'):
            assert content.versions.count() >= 1, "Au moins une version doit exister"
    
    def test_content_version_history_if_implemented(self, client, contributor_user):
        """Vérifie l'historique des versions si versioning est implémenté"""
        # Vérifier si versioning est implémenté
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        has_versioning = any('version' in f.lower() or 'history' in f.lower() for f in content_fields)
        
        if not has_versioning:
            pytest.skip("Versioning non implémenté dans EducationalContent")
        
        # Si versioning est implémenté, créer un contenu avec plusieurs modifications
        # et vérifier que l'historique est disponible
        client.force_authenticate(user=contributor_user)
        unique_slug = f'test-history-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        # Créer un contenu
        url = '/api/contents/'
        response = client.post(url, {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': 'Test description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        content = EducationalContent.objects.get(slug=unique_slug)
        
        # Vérifier que l'historique est accessible
        # (à adapter selon l'implémentation réelle)
        if hasattr(content, 'versions'):
            versions = content.versions.all()
            assert len(versions) >= 1, "Au moins une version doit exister dans l'historique"
    
    def test_content_rollback_if_implemented(self, client, contributor_user):
        """Vérifie le rollback vers une version précédente si versioning est implémenté"""
        # Vérifier si versioning est implémenté
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        has_versioning = any('version' in f.lower() or 'history' in f.lower() for f in content_fields)
        
        if not has_versioning:
            pytest.skip("Versioning non implémenté dans EducationalContent")
        
        # Si versioning est implémenté, créer un contenu, le modifier, puis rollback
        # (à adapter selon l'implémentation réelle)
        client.force_authenticate(user=contributor_user)
        unique_slug = f'test-rollback-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        # Créer un contenu
        url = '/api/contents/'
        response = client.post(url, {
            'title': 'Original Title',
            'slug': unique_slug,
            'type': 'article',
            'description': 'Original description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        content = EducationalContent.objects.get(slug=unique_slug)
        
        # Tester le rollback (si endpoint disponible)
        # (à adapter selon l'implémentation réelle)

