"""
Tests pour les exports institutionnels (ONU / Fondation).

Vérifie :
- Format JSON valide
- Contenu minimal présent
- Cohérence versions docs
- Schéma valide
"""
import json
import pytest
from django.test import TestCase, Client
from django.core.cache import cache
from django.contrib.auth.models import User
from core.models import SakaWallet, SakaTransaction, AuditLog
from finance.models import UserWallet
from core.models.alerts import CriticalAlertEvent


@pytest.fixture
def client():
    """Client API pour les tests"""
    return Client()


@pytest.mark.django_db
@pytest.mark.critical
class TestUNComplianceExport:
    """Tests pour l'export conformité ONU"""
    
    def test_endpoint_accessible_sans_authentification(self, client):
        """Vérifie que l'endpoint est accessible sans authentification"""
        response = client.get('/api/compliance/export/un/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json; charset=utf-8'
    
    def test_format_json_valide(self, client):
        """Vérifie que la réponse est un JSON valide"""
        response = client.get('/api/compliance/export/un/')
        assert response.status_code == 200
        
        try:
            data = json.loads(response.content)
            assert isinstance(data, dict)
        except json.JSONDecodeError as e:
            pytest.fail(f"La réponse n'est pas un JSON valide: {e}")
    
    def test_schema_valide(self, client):
        """Vérifie que le schéma JSON est valide"""
        response = client.get('/api/compliance/export/un/')
        data = json.loads(response.content)
        
        # Vérifier les champs obligatoires
        assert 'export_type' in data
        assert 'version' in data
        assert 'generated_at' in data
        assert 'project' in data
        assert 'sections' in data
        
        # Vérifier les sections
        sections = data.get('sections', {})
        assert 'gouvernance' in sections
        assert 'separation_saka_eur' in sections
        assert 'anti_accumulation' in sections
        assert 'audits' in sections
        assert 'alerting' in sections
    
    def test_contenu_minimal_present(self, client):
        """Vérifie que le contenu minimal est présent"""
        response = client.get('/api/compliance/export/un/')
        data = json.loads(response.content)
        
        # Vérifier gouvernance
        governance = data['sections']['gouvernance']
        assert 'constitution' in governance
        assert 'think_tank_charter' in governance
        assert 'separation_of_powers' in governance
        
        # Vérifier séparation SAKA/EUR
        separation = data['sections']['separation_saka_eur']
        assert 'separation_verified' in separation
        assert 'technical_checks' in separation
        assert 'tests_status' in separation
        
        # Vérifier anti-accumulation
        anti_accum = data['sections']['anti_accumulation']
        assert 'composting_enabled' in anti_accum
        assert 'redistribution_enabled' in anti_accum
        assert 'metrics' in anti_accum
        
        # Vérifier audits
        audits = data['sections']['audits']
        assert 'audit_logs' in audits
        assert 'traceability' in audits
        
        # Vérifier alerting
        alerting = data['sections']['alerting']
        assert 'mechanisms' in alerting
        assert 'metrics' in alerting
        assert 'deduplication' in alerting
    
    def test_coherence_versions_docs(self, client):
        """Vérifie la cohérence des versions de documents"""
        response = client.get('/api/compliance/export/un/')
        data = json.loads(response.content)
        
        governance = data['sections']['gouvernance']
        
        # Vérifier que les versions sont cohérentes
        constitution_version = governance.get('constitution', {}).get('version')
        think_tank_version = governance.get('think_tank_charter', {}).get('version')
        institute_version = governance.get('institute_role', {}).get('version')
        
        # Les versions doivent être présentes (peuvent être différentes)
        assert constitution_version is not None
        assert think_tank_version is not None
        assert institute_version is not None
    
    def test_compliance_badge_present(self, client):
        """Vérifie que le badge de conformité est présent"""
        response = client.get('/api/compliance/export/un/')
        data = json.loads(response.content)
        
        assert 'compliance_badge' in data
        assert 'url' in data['compliance_badge']
        assert 'status_endpoint' in data['compliance_badge']


@pytest.mark.django_db
@pytest.mark.critical
class TestFoundationReportExport:
    """Tests pour l'export rapport Fondation"""
    
    def test_endpoint_accessible_sans_authentification(self, client):
        """Vérifie que l'endpoint est accessible sans authentification"""
        response = client.get('/api/compliance/export/foundation/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json; charset=utf-8'
    
    def test_format_json_valide(self, client):
        """Vérifie que la réponse est un JSON valide"""
        response = client.get('/api/compliance/export/foundation/')
        assert response.status_code == 200
        
        try:
            data = json.loads(response.content)
            assert isinstance(data, dict)
        except json.JSONDecodeError as e:
            pytest.fail(f"La réponse n'est pas un JSON valide: {e}")
    
    def test_schema_valide(self, client):
        """Vérifie que le schéma JSON est valide"""
        response = client.get('/api/compliance/export/foundation/')
        data = json.loads(response.content)
        
        # Vérifier les champs obligatoires
        assert 'export_type' in data
        assert data['export_type'] == 'foundation_report'
        assert 'version' in data
        assert 'generated_at' in data
        assert 'sections' in data
        assert 'foundation_specific' in data
    
    def test_foundation_specific_section(self, client):
        """Vérifie que la section foundation_specific est présente"""
        response = client.get('/api/compliance/export/foundation/')
        data = json.loads(response.content)
        
        foundation_specific = data.get('foundation_specific', {})
        assert 'transparency' in foundation_specific
        assert 'compliance_badge' in foundation_specific


@pytest.mark.django_db
class TestInstitutionalMarkdownExport:
    """Tests pour l'export Markdown"""
    
    def test_un_markdown_export(self, client):
        """Vérifie l'export Markdown ONU"""
        response = client.get('/api/compliance/export/un/markdown/')
        assert response.status_code == 200
        assert 'text/markdown' in response['Content-Type']
        
        content = response.content.decode('utf-8')
        assert '# Rapport de Conformité EGOEJO - UN' in content
        assert '## 1. Gouvernance' in content
        assert '## 2. Séparation SAKA/EUR' in content
        assert '## 3. Anti-Accumulation' in content
        assert '## 4. Audits' in content
        assert '## 5. Alerting' in content
    
    def test_foundation_markdown_export(self, client):
        """Vérifie l'export Markdown Fondation"""
        response = client.get('/api/compliance/export/foundation/markdown/')
        assert response.status_code == 200
        assert 'text/markdown' in response['Content-Type']
        
        content = response.content.decode('utf-8')
        assert '# Rapport de Conformité EGOEJO - FOUNDATION' in content


@pytest.mark.django_db
class TestExportCache:
    """Tests pour le cache des exports"""
    
    def test_cache_controle(self, client):
        """Vérifie que le cache est correctement utilisé"""
        cache.clear()
        
        # Premier appel
        response1 = client.get('/api/compliance/export/un/')
        assert response1.status_code == 200
        assert 'Cache-Control' in response1
        assert 'public, max-age=900' in response1['Cache-Control']
        
        # Deuxième appel (devrait utiliser le cache)
        response2 = client.get('/api/compliance/export/un/')
        assert response2.status_code == 200
        
        # Les contenus doivent être identiques (même generated_at)
        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)
        assert data1['generated_at'] == data2['generated_at']


@pytest.mark.django_db
class TestExportReadOnly:
    """Tests pour vérifier que les exports sont en lecture seule"""
    
    def test_post_not_allowed(self, client):
        """Vérifie que POST n'est pas autorisé"""
        response = client.post('/api/compliance/export/un/')
        assert response.status_code in [405, 301]  # Method Not Allowed ou redirect
    
    def test_put_not_allowed(self, client):
        """Vérifie que PUT n'est pas autorisé"""
        response = client.put('/api/compliance/export/un/')
        assert response.status_code in [405, 301]
    
    def test_delete_not_allowed(self, client):
        """Vérifie que DELETE n'est pas autorisé"""
        response = client.delete('/api/compliance/export/un/')
        assert response.status_code in [405, 301]

