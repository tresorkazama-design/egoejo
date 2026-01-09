"""
Tests unitaires pour la validation fail-fast des settings SAKA.

Ces tests vérifient que toute valeur invalide lève ImproperlyConfigured
au démarrage Django.
"""
import pytest
import sys
import os
import importlib
from django.core.exceptions import ImproperlyConfigured


def _reload_settings_module():
    """Force le rechargement du module settings en nettoyant tous les modules config."""
    # Supprimer tous les modules config.*
    modules_to_remove = [key for key in list(sys.modules.keys()) if key.startswith('config.')]
    for module_name in modules_to_remove:
        del sys.modules[module_name]
    # Nettoyer le cache Django settings si présent
    if 'django.conf' in sys.modules:
        if hasattr(sys.modules['django.conf'], '_wrapped'):
            delattr(sys.modules['django.conf'], '_wrapped')
    # Recharger le module
    return importlib.import_module('config.settings')


@pytest.mark.egoejo_compliance
class TestSettingsFailFast:
    """
    Tests de validation fail-fast : Toute valeur invalide doit lever ImproperlyConfigured.
    """
    
    def test_saka_compost_rate_zero_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_RATE = 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '0.0')
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_RATE doit être strictement supérieur à 0"):
            _reload_settings_module()
    
    def test_saka_compost_rate_negatif_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_RATE < 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '-0.1')
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_RATE doit être strictement supérieur à 0"):
            _reload_settings_module()
    
    def test_saka_compost_rate_superieur_un_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_RATE > 1.0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '1.5')
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_RATE doit être strictement supérieur à 0"):
            _reload_settings_module()
    
    def test_saka_compost_rate_valide_ne_leve_pas_exception(self, monkeypatch):
        """SAKA_COMPOST_RATE entre 0 et 1 (exclusif pour 0) ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '0.1')
        settings = _reload_settings_module()
        assert settings.SAKA_COMPOST_RATE == 0.1
    
    def test_saka_compost_rate_un_valide(self, monkeypatch):
        """SAKA_COMPOST_RATE = 1.0 est valide."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '1.0')
        settings = _reload_settings_module()
        assert settings.SAKA_COMPOST_RATE == 1.0
    
    def test_saka_compost_inactivity_days_zero_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS = 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '0')
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365"):
            _reload_settings_module()
    
    def test_saka_compost_inactivity_days_negatif_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS < 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '-1')
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365"):
            _reload_settings_module()
    
    def test_saka_compost_inactivity_days_superieur_365_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS > 365 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '366')
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365"):
            _reload_settings_module()
    
    def test_saka_compost_inactivity_days_valide_ne_leve_pas_exception(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS entre 1 et 365 ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '90')
        settings = _reload_settings_module()
        assert settings.SAKA_COMPOST_INACTIVITY_DAYS == 90
    
    def test_saka_compost_inactivity_days_un_valide(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS = 1 est valide."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '1')
        settings = _reload_settings_module()
        assert settings.SAKA_COMPOST_INACTIVITY_DAYS == 1
    
    def test_saka_compost_inactivity_days_365_valide(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS = 365 est valide."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '365')
        settings = _reload_settings_module()
        assert settings.SAKA_COMPOST_INACTIVITY_DAYS == 365
    
    def test_saka_silo_redis_rate_zero_leve_improperly_configured(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE = 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.0')
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0"):
            _reload_settings_module()
    
    def test_saka_silo_redis_rate_negatif_leve_improperly_configured(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE < 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '-0.05')
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0"):
            _reload_settings_module()
    
    def test_saka_silo_redis_rate_superieur_un_leve_improperly_configured(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE > 1.0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '1.5')
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0"):
            _reload_settings_module()
    
    def test_saka_silo_redis_rate_valide_ne_leve_pas_exception(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE entre 0 et 1 (exclusif pour 0) ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.05')
        settings = _reload_settings_module()
        assert settings.SAKA_SILO_REDIS_RATE == 0.05
    
    def test_saka_silo_redis_rate_un_valide(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE = 1.0 est valide."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '1.0')
        settings = _reload_settings_module()
        assert settings.SAKA_SILO_REDIS_RATE == 1.0
    
    def test_saka_silo_redis_enabled_avec_rate_invalide_leve_improperly_configured(self, monkeypatch):
        """Si SAKA_SILO_REDIS_ENABLED = True et SAKA_SILO_REDIS_RATE invalide, doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_ENABLED', 'True')
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.0')
        # La validation de SAKA_SILO_REDIS_RATE se déclenche avant la validation combinée
        # donc on accepte les deux messages d'erreur possibles
        with pytest.raises(ImproperlyConfigured, match="(SAKA_SILO_REDIS_ENABLED est True mais SAKA_SILO_REDIS_RATE est invalide|SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0)"):
            _reload_settings_module()
    
    def test_saka_silo_redis_enabled_avec_rate_valide_ne_leve_pas_exception(self, monkeypatch):
        """Si SAKA_SILO_REDIS_ENABLED = True et SAKA_SILO_REDIS_RATE valide, ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_SILO_REDIS_ENABLED', 'True')
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.05')
        settings = _reload_settings_module()
        assert settings.SAKA_SILO_REDIS_ENABLED is True
        assert settings.SAKA_SILO_REDIS_RATE == 0.05
