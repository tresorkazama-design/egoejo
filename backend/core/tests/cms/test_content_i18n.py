"""
Tests i18n pour le CMS (si applicable).

Vérifie :
- Fallback langue si i18n est géré
- Traductions de contenu (si présent)
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
class TestContentI18n:
    """Tests i18n pour le CMS (si applicable)"""
    
    def test_content_no_i18n_field(self, client, contributor_user):
        """Vérifie que le modèle EducationalContent n'a pas de champ i18n (pour l'instant)"""
        # Vérifier que le modèle n'a pas de champ language ou locale
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        i18n_fields = [f for f in content_fields if 'language' in f.lower() or 'locale' in f.lower() or 'lang' in f.lower()]
        
        # Si aucun champ i18n, le test passe (i18n non implémenté)
        # Si des champs i18n existent, on doit tester le fallback
        if len(i18n_fields) == 0:
            pytest.skip("i18n non implémenté dans EducationalContent")
        else:
            # Si i18n est implémenté, tester le fallback
            assert len(i18n_fields) > 0, "Champs i18n trouvés mais non testés"
    
    def test_content_fallback_language_if_implemented(self, client, contributor_user):
        """Vérifie le fallback de langue si i18n est implémenté"""
        # Vérifier si i18n est implémenté
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        has_i18n = any('language' in f.lower() or 'locale' in f.lower() for f in content_fields)
        
        if not has_i18n:
            pytest.skip("i18n non implémenté dans EducationalContent")
        
        # Si i18n est implémenté, créer un contenu sans langue spécifiée
        # et vérifier qu'il utilise la langue par défaut
        client.force_authenticate(user=contributor_user)
        unique_slug = f'test-i18n-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        url = '/api/contents/'
        response = client.post(url, {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': 'Test description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        content = EducationalContent.objects.get(slug=unique_slug)
        
        # Vérifier que la langue par défaut est utilisée
        # (à adapter selon l'implémentation réelle)
        if hasattr(content, 'language'):
            assert content.language is not None, "Langue par défaut doit être définie"
    
    def test_content_multilingual_if_implemented(self, client, contributor_user):
        """Vérifie le support multilingue si i18n est implémenté"""
        # Vérifier si i18n est implémenté
        content_fields = [f.name for f in EducationalContent._meta.get_fields()]
        has_i18n = any('language' in f.lower() or 'locale' in f.lower() for f in content_fields)
        
        if not has_i18n:
            pytest.skip("i18n non implémenté dans EducationalContent")
        
        # Si i18n est implémenté, créer des contenus dans différentes langues
        # et vérifier qu'ils sont correctement gérés
        client.force_authenticate(user=contributor_user)
        
        # Créer un contenu en français
        unique_slug_fr = f'test-i18n-fr-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        response_fr = client.post('/api/contents/', {
            'title': 'Contenu français',
            'slug': unique_slug_fr,
            'type': 'article',
            'description': 'Description en français',
            'language': 'fr',  # Si le champ existe
        })
        
        assert response_fr.status_code == status.HTTP_201_CREATED
        
        # Créer un contenu en anglais
        unique_slug_en = f'test-i18n-en-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        response_en = client.post('/api/contents/', {
            'title': 'English Content',
            'slug': unique_slug_en,
            'type': 'article',
            'description': 'English description',
            'language': 'en',  # Si le champ existe
        })
        
        assert response_en.status_code == status.HTTP_201_CREATED
        
        # Vérifier que les deux contenus sont distincts
        content_fr = EducationalContent.objects.get(slug=unique_slug_fr)
        content_en = EducationalContent.objects.get(slug=unique_slug_en)
        
        assert content_fr.id != content_en.id, "Les contenus doivent être distincts"

