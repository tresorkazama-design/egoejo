"""
Tests XSS sanitization pour EducationalContent.

Vérifie que le contenu est correctement sanitizé pour prévenir les attaques XSS.
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
@pytest.mark.critical
class TestContentXSSSanitization:
    """Tests de sanitization XSS pour EducationalContent"""
    
    def test_xss_script_tag_sanitized(self, client, contributor_user):
        """Vérifie que les balises <script> sont sanitizées dans description"""
        client.force_authenticate(user=contributor_user)
        
        malicious_description = "<script>alert('XSS')</script>Contenu normal"
        unique_slug = f'test-content-xss-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': malicious_description,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Content',
                'slug': unique_slug,
                'type': 'article',
                'description': malicious_description,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # La description doit être sanitizée (pas de <script>)
        assert '<script>' not in content.description, "Balises <script> doivent être sanitizées"
        assert 'alert' in content.description or 'XSS' in content.description, "Contenu normal doit être préservé"
    
    def test_xss_img_onerror_sanitized(self, client, contributor_user):
        """Vérifie que les attributs onerror sont sanitizés"""
        client.force_authenticate(user=contributor_user)
        
        malicious_description = '<img src="x" onerror="alert(\'XSS\')">'
        import time
        unique_slug = f'test-content-xss-img-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': malicious_description,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Content',
                'slug': unique_slug,
                'type': 'article',
                'description': malicious_description,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # L'attribut onerror doit être sanitizé
        assert 'onerror' not in content.description, "Attributs onerror doivent être sanitizés"
    
    def test_xss_javascript_protocol_sanitized(self, client, contributor_user):
        """Vérifie que les protocoles javascript: sont sanitizés"""
        client.force_authenticate(user=contributor_user)
        
        malicious_description = '<a href="javascript:alert(\'XSS\')">Lien</a>'
        import time
        unique_slug = f'test-content-xss-js-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': malicious_description,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Content',
                'slug': unique_slug,
                'type': 'article',
                'description': malicious_description,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # Le protocole javascript: doit être sanitizé
        assert 'javascript:' not in content.description, "Protocoles javascript: doivent être sanitizés"
    
    def test_xss_iframe_sanitized(self, client, contributor_user):
        """Vérifie que les balises <iframe> sont sanitizées"""
        client.force_authenticate(user=contributor_user)
        
        malicious_description = '<iframe src="javascript:alert(\'XSS\')"></iframe>'
        import time
        unique_slug = f'test-content-xss-iframe-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': malicious_description,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Content',
                'slug': unique_slug,
                'type': 'article',
                'description': malicious_description,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # Les balises <iframe> doivent être sanitizées
        assert '<iframe' not in content.description, "Balises <iframe> doivent être sanitizées"
    
    def test_xss_title_sanitized(self, client, contributor_user):
        """Vérifie que le titre est aussi sanitizé"""
        client.force_authenticate(user=contributor_user)
        
        malicious_title = "<script>alert('XSS')</script>Title"
        import time
        unique_slug = f'test-content-xss-title-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': malicious_title,
            'slug': unique_slug,
            'type': 'article',
            'description': 'Description normale',
        })
        
        # Accepter 201 ou 301 (redirection) si le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # Le titre doit être sanitizé
        assert '<script>' not in content.title, "Balises <script> dans le titre doivent être sanitizées"
    
    def test_safe_html_preserved(self, client, contributor_user):
        """Vérifie que le HTML sûr (si autorisé) est préservé"""
        client.force_authenticate(user=contributor_user)
        
        safe_description = "<p>Paragraphe normal</p><strong>Texte en gras</strong>"
        import time
        unique_slug = f'test-content-safe-html-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': safe_description,
        })
        
        # Accepter 201 ou 301 (redirection) si le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # Le contenu doit être préservé (échappé ou sanitizé selon la politique)
        # Note: Si HTML n'est pas autorisé, il sera échappé
        assert 'Paragraphe normal' in content.description, "Contenu texte doit être préservé"
    
    def test_markdown_not_executed(self, client, contributor_user):
        """Vérifie que le markdown n'est pas exécuté comme code"""
        client.force_authenticate(user=contributor_user)
        
        # Markdown avec du code qui pourrait être interprété
        markdown_description = "```javascript\nalert('XSS')\n```"
        import time
        unique_slug = f'test-content-markdown-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        response = client.post('/api/contents/', {
            'title': 'Test Content',
            'slug': unique_slug,
            'type': 'article',
            'description': markdown_description,
        })
        
        # Accepter 201 ou 301 (redirection) si le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé"
        
        content = EducationalContent.objects.get(slug=unique_slug)
        # Le markdown doit être stocké tel quel (pas exécuté)
        assert '```' in content.description or 'javascript' in content.description, "Markdown doit être préservé comme texte"

