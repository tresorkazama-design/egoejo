"""
Tests pour vérifier que update() est bloqué sur SakaWallet.

Constitution EGOEJO: no direct SAKA mutation.
La méthode update() doit être strictement interdite pour garantir la traçabilité.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.models.saka import SakaWallet, AllowSakaMutation

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaWalletUpdatePrevention:
    """Tests pour vérifier que update() est bloqué sur SakaWallet"""
    
    def test_update_without_protected_fields_raises_error(self):
        """Même sans modifier de champs protégés, update() doit être bloqué"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer ou récupérer un wallet
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        
        # Tenter un update() même sans modifier de champs protégés
        # (par exemple, modifier updated_at ou last_activity_date)
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.filter(pk=wallet.pk).update(last_activity_date=None)
        
        assert "Direct update() is forbidden on SakaWallet" in str(exc_info.value)
        assert "Use SakaTransaction service" in str(exc_info.value)
    
    def test_update_with_protected_fields_raises_error(self):
        """update() avec champs protégés doit être bloqué"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Créer ou récupérer un wallet
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        
        # Tenter un update() avec un champ protégé
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.filter(pk=wallet.pk).update(balance=200)
        
        assert "Direct update() is forbidden on SakaWallet" in str(exc_info.value)
        assert "Use SakaTransaction service" in str(exc_info.value)
    
    def test_update_multiple_protected_fields_raises_error(self):
        """update() avec plusieurs champs protégés doit être bloqué"""
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        # Créer ou récupérer un wallet
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        
        # Tenter un update() avec plusieurs champs protégés
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.filter(pk=wallet.pk).update(
                balance=200,
                total_harvested=200,
                total_planted=50
            )
        
        assert "Direct update() is forbidden on SakaWallet" in str(exc_info.value)
        assert "Use SakaTransaction service" in str(exc_info.value)
    
    def test_update_all_wallets_raises_error(self):
        """update() sur tous les wallets doit être bloqué"""
        user1 = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpass123'
        )
        user2 = User.objects.create_user(
            username='testuser5',
            email='test5@example.com',
            password='testpass123'
        )
        
        # Créer ou récupérer deux wallets
        SakaWallet.objects.get_or_create(
            user=user1,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        SakaWallet.objects.get_or_create(
            user=user2,
            defaults={
                'balance': 200,
                'total_harvested': 200,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        
        # Tenter un update() sur tous les wallets
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.all().update(balance=0)
        
        assert "Direct update() is forbidden on SakaWallet" in str(exc_info.value)
        assert "Use SakaTransaction service" in str(exc_info.value)
    
    def test_update_with_allow_saka_mutation_still_raises_error(self):
        """
        Même avec AllowSakaMutation, update() doit être bloqué.
        
        Note: AllowSakaMutation est pour .save(), pas pour .update().
        La méthode update() est strictement interdite pour garantir la traçabilité.
        """
        user = User.objects.create_user(
            username='testuser6',
            email='test6@example.com',
            password='testpass123'
        )
        
        # Créer ou récupérer un wallet
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        
        # Tenter un update() même avec AllowSakaMutation
        # (AllowSakaMutation ne doit pas permettre update())
        with AllowSakaMutation():
            with pytest.raises(ValidationError) as exc_info:
                SakaWallet.objects.filter(pk=wallet.pk).update(balance=200)
            
            assert "Direct update() is forbidden on SakaWallet" in str(exc_info.value)
            assert "Use SakaTransaction service" in str(exc_info.value)
    
    def test_update_with_empty_kwargs_still_raises_error(self):
        """update() avec kwargs vides doit quand même être bloqué"""
        user = User.objects.create_user(
            username='testuser7',
            email='test7@example.com',
            password='testpass123'
        )
        
        # Créer ou récupérer un wallet
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0
            }
        )
        
        # Tenter un update() avec kwargs vides (cas limite)
        # Note: En pratique, update() sans kwargs ne fait rien, mais on bloque quand même
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.filter(pk=wallet.pk).update()
        
        assert "Direct update() is forbidden on SakaWallet" in str(exc_info.value)
        assert "Use SakaTransaction service" in str(exc_info.value)

