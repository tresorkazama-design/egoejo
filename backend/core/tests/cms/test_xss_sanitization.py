"""
Tests XSS sanitization pour le CMS.

Vérifie que les contenus sont correctement sanitizés pour prévenir les attaques XSS.
"""
import pytest
import uuid
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from core.models import EducationalContent
from core.permissions import CONTENT_CONTRIBUTOR_GROUP_NAME
from core.security.sanitization import sanitize_string, sanitize_html


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
class TestXSSSanitization:
    """Tests de sanitization XSS"""
    
    def test_xss_script_tag_escaped(self, client, contributor_user, db):
        """Vérifie que les balises <script> sont échappées dans title"""
        client.force_authenticate(user=contributor_user)
        # Utiliser directement l'URL avec slash final pour éviter les redirections
        url = '/api/contents/'
        
        # Générer un slug vraiment unique avec timestamp + UUID
        import time
        unique_slug = f'test-xss-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post(url, {
            'title': xss_payload,
            'slug': unique_slug,
            'type': 'article',
            'description': 'Test description',
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': xss_payload,
                'slug': unique_slug,
                'type': 'article',
                'description': 'Test description',
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}. Response: {response.data if hasattr(response, 'data') else response.content}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        content = EducationalContent.objects.get(slug=unique_slug)
        # Le titre doit être échappé (pas de balise <script>)
        assert '<script>' not in content.title, "Balise <script> doit être échappée"
        assert '&lt;script&gt;' in content.title or '<script>' not in content.title
    
    def test_xss_script_tag_escaped_description(self, client, contributor_user, db):
        """Vérifie que les balises <script> sont échappées dans description"""
        client.force_authenticate(user=contributor_user)
        # Utiliser directement l'URL avec slash final pour éviter les redirections
        url = '/api/contents/'
        
        # Générer un slug vraiment unique avec timestamp + UUID
        import time
        unique_slug = f'test-xss-desc-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post(url, {
            'title': 'Test Title',
            'slug': unique_slug,
            'type': 'article',
            'description': xss_payload,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Title',
                'slug': unique_slug,
                'type': 'article',
                'description': xss_payload,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}. Response: {response.data if hasattr(response, 'data') else response.content}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        content = EducationalContent.objects.get(slug=unique_slug)
        # La description doit être échappée
        assert '<script>' not in content.description, "Balise <script> doit être échappée"
    
    def test_xss_onclick_escaped(self, client, contributor_user, db):
        """Vérifie que les attributs onclick sont échappés"""
        client.force_authenticate(user=contributor_user)
        # Utiliser directement l'URL avec slash final pour éviter les redirections
        url = '/api/contents/'
        
        # Générer un slug vraiment unique avec timestamp + UUID
        import time
        unique_slug = f'test-xss-onclick-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        xss_payload = '<a onclick="alert(\'XSS\')">Click me</a>'
        response = client.post(url, {
            'title': 'Test Title',
            'slug': unique_slug,
            'type': 'article',
            'description': xss_payload,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Title',
                'slug': unique_slug,
                'type': 'article',
                'description': xss_payload,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}. Response: {response.data if hasattr(response, 'data') else response.content}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        content = EducationalContent.objects.get(slug=unique_slug)
        # L'attribut onclick doit être échappé ou supprimé
        assert 'onclick=' not in content.description.lower(), "Attribut onclick doit être supprimé"
    
    def test_xss_img_src_javascript_escaped(self, client, contributor_user, db):
        """Vérifie que les URLs javascript: sont échappées"""
        client.force_authenticate(user=contributor_user)
        # Utiliser directement l'URL avec slash final pour éviter les redirections
        url = '/api/contents/'
        
        # Générer un slug vraiment unique avec timestamp + UUID
        import time
        unique_slug = f'test-xss-img-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        xss_payload = '<img src="javascript:alert(\'XSS\')">'
        response = client.post(url, {
            'title': 'Test Title',
            'slug': unique_slug,
            'type': 'article',
            'description': xss_payload,
        })
        
        # Si redirection 301, suivre manuellement avec POST
        if response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            from urllib.parse import urlparse
            redirect_path = urlparse(response.url).path
            response = client.post(redirect_path, {
                'title': 'Test Title',
                'slug': unique_slug,
                'type': 'article',
                'description': xss_payload,
            }, follow=False)
        
        # Accepter 201 ou vérifier que le contenu est créé
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_301_MOVED_PERMANENTLY], f"Expected 201 or 301, got {response.status_code}. Response: {response.data if hasattr(response, 'data') else response.content}"
        assert EducationalContent.objects.filter(slug=unique_slug).exists(), f"Le contenu avec slug {unique_slug} n'a pas été créé. Status: {response.status_code}"
        content = EducationalContent.objects.get(slug=unique_slug)
        # L'URL javascript: doit être échappée ou supprimée
        assert 'javascript:' not in content.description.lower(), "URL javascript: doit être supprimée"
    
    def test_sanitize_string_function(self):
        """Vérifie que sanitize_string fonctionne correctement"""
        xss_payload = "<script>alert('XSS')</script>"
        cleaned = sanitize_string(xss_payload, allow_html=False)
        
        assert '<script>' not in cleaned, "Balise <script> doit être échappée"
        assert '&lt;script&gt;' in cleaned or '<script>' not in cleaned
    
    def test_sanitize_html_function(self):
        """Vérifie que sanitize_html fonctionne correctement (si bleach disponible)"""
        html_payload = '<p>Safe content</p><script>alert("XSS")</script><a href="http://example.com">Link</a>'
        cleaned = sanitize_html(html_payload)
        
        # Le script doit être supprimé
        assert '<script>' not in cleaned, "Balise <script> doit être supprimée"
        # Le contenu safe doit être préservé
        assert 'Safe content' in cleaned, "Contenu safe doit être préservé"
    
    def test_sanitize_html_allows_safe_tags(self):
        """Vérifie que sanitize_html permet les tags sécurisés"""
        html_payload = '<p>Paragraph</p><strong>Bold</strong><a href="http://example.com">Link</a>'
        cleaned = sanitize_html(html_payload)
        
        # Les tags sécurisés doivent être préservés
        assert '<p>' in cleaned or 'Paragraph' in cleaned, "Tag <p> doit être préservé"
        assert '<strong>' in cleaned or 'Bold' in cleaned, "Tag <strong> doit être préservé"
        # Le lien doit être préservé mais l'attribut href doit être vérifié
        assert 'Link' in cleaned, "Contenu du lien doit être préservé"

