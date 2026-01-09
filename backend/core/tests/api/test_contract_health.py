"""
Contract tests pour l'endpoint /api/health/

Vérifie que l'endpoint respecte son contrat :
- Status codes attendus (200, 503)
- Champs obligatoires dans la réponse
- Structure JSON valide
"""
import pytest
from django.test import Client
from django.db import connection
from django.core.cache import cache


@pytest.mark.django_db
@pytest.mark.critical
class TestHealthContract:
    """Tests contract pour /api/health/"""
    
    def test_health_endpoint_returns_200_when_healthy(self, client):
        """Vérifie que /api/health/ retourne 200 avec structure attendue"""
        response = client.get('/api/health/', follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Vérifier champs obligatoires
        assert 'status' in data, "Champ 'status' manquant"
        assert 'database' in data, "Champ 'database' manquant"
        assert 'service' in data, "Champ 'service' manquant"
        
        # Vérifier valeurs attendues
        assert data['status'] in ['ok', 'warning', 'error'], f"Status invalide: {data['status']}"
        assert data['service'] == 'egoejo-backend', f"Service invalide: {data['service']}"
    
    def test_health_endpoint_has_required_fields(self, client):
        """Vérifie que tous les champs obligatoires sont présents"""
        response = client.get('/api/health/', follow=True)
        data = response.json()
        
        required_fields = ['status', 'database', 'service']
        for field in required_fields:
            assert field in data, f"Champ obligatoire '{field}' manquant"
    
    def test_health_endpoint_returns_json(self, client):
        """Vérifie que la réponse est du JSON valide"""
        response = client.get('/api/health/', follow=True)
        
        assert 'application/json' in response['Content-Type'], f"Content-Type doit être application/json, got {response['Content-Type']}"
        assert isinstance(response.json(), dict), "La réponse doit être un objet JSON"
    
    def test_health_endpoint_handles_database_error(self, client, monkeypatch):
        """Vérifie que l'endpoint gère correctement les erreurs DB (503)"""
        # Simuler une erreur DB en patchant connection.cursor
        original_cursor = connection.cursor
        
        def mock_cursor_error():
            raise Exception("Database connection failed")
        
        monkeypatch.setattr(connection, 'cursor', lambda: mock_cursor_error())
        
        try:
            response = client.get('/api/health/', follow=True)
            
            # L'endpoint doit retourner 503 en cas d'erreur DB
            assert response.status_code in [503, 500], f"Expected 503 or 500, got {response.status_code}"
            data = response.json()
            assert 'status' in data
            assert data['status'] in ['error', 'warning'], f"Status doit être 'error' ou 'warning', got {data['status']}"
        finally:
            # Restaurer le cursor original
            monkeypatch.setattr(connection, 'cursor', original_cursor)

