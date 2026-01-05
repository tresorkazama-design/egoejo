"""
Tests unitaires pour la validation fail-fast des settings SAKA.

Ces tests vérifient que toute valeur invalide lève ImproperlyConfigured
au démarrage Django.
"""
import pytest
import sys
import os
from django.core.exceptions import ImproperlyConfigured


@pytest.mark.egoejo_compliance
class TestSettingsFailFast:
    """
    Tests de validation fail-fast : Toute valeur invalide doit lever ImproperlyConfigured.
    """
    
    def test_saka_compost_rate_zero_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_RATE = 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '0.0')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_RATE doit être strictement supérieur à 0"):
            from config import settings
    
    def test_saka_compost_rate_negatif_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_RATE < 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '-0.1')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_RATE doit être strictement supérieur à 0"):
            from config import settings
    
    def test_saka_compost_rate_superieur_un_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_RATE > 1.0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '1.5')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_RATE doit être strictement supérieur à 0"):
            from config import settings
    
    def test_saka_compost_rate_valide_ne_leve_pas_exception(self, monkeypatch):
        """SAKA_COMPOST_RATE entre 0 et 1 (exclusif pour 0) ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '0.1')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_COMPOST_RATE == 0.1
    
    def test_saka_compost_rate_un_valide(self, monkeypatch):
        """SAKA_COMPOST_RATE = 1.0 est valide."""
        monkeypatch.setenv('SAKA_COMPOST_RATE', '1.0')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_COMPOST_RATE == 1.0
    
    def test_saka_compost_inactivity_days_zero_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS = 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '0')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365"):
            from config import settings
    
    def test_saka_compost_inactivity_days_negatif_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS < 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '-1')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365"):
            from config import settings
    
    def test_saka_compost_inactivity_days_superieur_365_leve_improperly_configured(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS > 365 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '366')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365"):
            from config import settings
    
    def test_saka_compost_inactivity_days_valide_ne_leve_pas_exception(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS entre 1 et 365 ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '90')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_COMPOST_INACTIVITY_DAYS == 90
    
    def test_saka_compost_inactivity_days_un_valide(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS = 1 est valide."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '1')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_COMPOST_INACTIVITY_DAYS == 1
    
    def test_saka_compost_inactivity_days_365_valide(self, monkeypatch):
        """SAKA_COMPOST_INACTIVITY_DAYS = 365 est valide."""
        monkeypatch.setenv('SAKA_COMPOST_INACTIVITY_DAYS', '365')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_COMPOST_INACTIVITY_DAYS == 365
    
    def test_saka_silo_redis_rate_zero_leve_improperly_configured(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE = 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.0')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0"):
            from config import settings
    
    def test_saka_silo_redis_rate_negatif_leve_improperly_configured(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE < 0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '-0.05')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0"):
            from config import settings
    
    def test_saka_silo_redis_rate_superieur_un_leve_improperly_configured(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE > 1.0 doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '1.5')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0"):
            from config import settings
    
    def test_saka_silo_redis_rate_valide_ne_leve_pas_exception(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE entre 0 et 1 (exclusif pour 0) ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.05')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_SILO_REDIS_RATE == 0.05
    
    def test_saka_silo_redis_rate_un_valide(self, monkeypatch):
        """SAKA_SILO_REDIS_RATE = 1.0 est valide."""
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '1.0')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_SILO_REDIS_RATE == 1.0
    
    def test_saka_silo_redis_enabled_avec_rate_invalide_leve_improperly_configured(self, monkeypatch):
        """Si SAKA_SILO_REDIS_ENABLED = True et SAKA_SILO_REDIS_RATE invalide, doit lever ImproperlyConfigured."""
        monkeypatch.setenv('SAKA_SILO_REDIS_ENABLED', 'True')
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.0')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        with pytest.raises(ImproperlyConfigured, match="SAKA_SILO_REDIS_ENABLED est True mais SAKA_SILO_REDIS_RATE est invalide"):
            from config import settings
    
    def test_saka_silo_redis_enabled_avec_rate_valide_ne_leve_pas_exception(self, monkeypatch):
        """Si SAKA_SILO_REDIS_ENABLED = True et SAKA_SILO_REDIS_RATE valide, ne doit pas lever d'exception."""
        monkeypatch.setenv('SAKA_SILO_REDIS_ENABLED', 'True')
        monkeypatch.setenv('SAKA_SILO_REDIS_RATE', '0.05')
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        from config import settings
        assert settings.SAKA_SILO_REDIS_ENABLED is True
        assert settings.SAKA_SILO_REDIS_RATE == 0.05
