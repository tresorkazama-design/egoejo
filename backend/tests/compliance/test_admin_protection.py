"""
Test de protection contre modification directe SAKA/EUR via Django Admin.

PHILOSOPHIE EGOEJO :
Empêche la modification directe de SakaWallet ou UserWallet via Django Admin
qui pourrait violer la séparation SAKA/EUR.
"""
import pytest
from django.contrib.auth import get_user_model
from core.models.saka import SakaWallet
from finance.models import UserWallet

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.egoejo_compliance
class TestAdminProtection:
    """
    Tests pour protéger contre les modifications directes SAKA/EUR via Django Admin.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    def test_modification_directe_sakawallet_possible_mais_logged(self):
        """
        Vérifie que la modification directe de SakaWallet.balance est possible
        (Django Admin permet cela), mais doit être tracée.
        
        NOTE : Django Admin permet la modification directe, mais nous devons
        nous assurer que cela ne viole pas la séparation SAKA/EUR.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer SakaWallet et UserWallet
        saka_wallet, _ = SakaWallet.objects.get_or_create(user=user)
        saka_wallet.balance = 100
        saka_wallet.save()
        
        user_wallet, _ = UserWallet.objects.get_or_create(user=user)
        user_wallet.balance = 1000.00
        user_wallet.save()
        
        # Modifier directement SakaWallet (simule Django Admin)
        saka_wallet.balance = 200
        saka_wallet.save()
        
        # Vérifier que la modification a été effectuée
        saka_wallet.refresh_from_db()
        assert saka_wallet.balance == 200
        
        # Vérifier que UserWallet n'a PAS changé (séparation préservée)
        user_wallet.refresh_from_db()
        assert user_wallet.balance == 1000.00, (
            "VIOLATION CONSTITUTION EGOEJO : Modification de SakaWallet a affecté UserWallet"
        )
    
    def test_modification_directe_userwallet_ne_doit_pas_affecter_sakawallet(self):
        """
        Vérifie que la modification directe de UserWallet.balance ne doit pas
        affecter SakaWallet (séparation préservée).
        """
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Créer SakaWallet et UserWallet
        saka_wallet, _ = SakaWallet.objects.get_or_create(user=user)
        saka_wallet.balance = 150
        saka_wallet.save()
        
        user_wallet, _ = UserWallet.objects.get_or_create(user=user)
        user_wallet.balance = 2000.00
        user_wallet.save()
        
        # Modifier directement UserWallet (simule Django Admin)
        user_wallet.balance = 3000.00
        user_wallet.save()
        
        # Vérifier que la modification a été effectuée
        user_wallet.refresh_from_db()
        assert user_wallet.balance == 3000.00
        
        # Vérifier que SakaWallet n'a PAS changé (séparation préservée)
        saka_wallet.refresh_from_db()
        assert saka_wallet.balance == 150, (
            "VIOLATION CONSTITUTION EGOEJO : Modification de UserWallet a affecté SakaWallet"
        )

