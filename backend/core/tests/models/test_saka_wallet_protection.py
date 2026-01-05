"""
Test de protection : SakaWallet empêche la modification directe des champs SAKA.

PHILOSOPHIE EGOEJO :
Empêche la modification directe de balance, total_harvested, total_planted, total_composted
sans passer par les services SAKA (harvest_saka, spend_saka, compost, redistribute).

Constitution: no direct SAKA mutation.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.models.saka import SakaWallet, AllowSakaMutation

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.egoejo_compliance
class TestSakaWalletProtection:
    """
    Tests pour vérifier que les champs SAKA ne peuvent pas être modifiés directement.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.fixture
    def test_user(self, db):
        """Utilisateur de test avec SakaWallet"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 200,
                'total_planted': 50,
                'total_composted': 30,
            }
        )
        return user, wallet
    
    def test_direct_balance_modification_raises_validation_error(self, test_user):
        """
        Vérifie que la modification directe de balance lève ValidationError.
        
        Constitution EGOEJO: no direct SAKA mutation.
        """
        user, wallet = test_user
        initial_balance = wallet.balance
        
        # Tentative de modification directe (sans AllowSakaMutation)
        wallet.balance = 9999
        
        # Doit lever ValidationError lors du save()
        with pytest.raises(ValidationError) as exc_info:
            wallet.save()
        
        # Vérifier le message d'erreur
        error_message = str(exc_info.value)
        assert "VIOLATION CONSTITUTION EGOEJO" in error_message
        assert "balance" in error_message
        assert "ne peuvent pas être modifiés directement" in error_message
        
        # Vérifier que le solde n'a pas changé en base
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance
    
    def test_direct_total_harvested_modification_raises_validation_error(self, test_user):
        """
        Vérifie que la modification directe de total_harvested lève ValidationError.
        """
        user, wallet = test_user
        initial_total_harvested = wallet.total_harvested
        
        # Tentative de modification directe
        wallet.total_harvested = 9999
        
        with pytest.raises(ValidationError) as exc_info:
            wallet.save()
        
        error_message = str(exc_info.value)
        assert "VIOLATION CONSTITUTION EGOEJO" in error_message
        assert "total_harvested" in error_message
        
        wallet.refresh_from_db()
        assert wallet.total_harvested == initial_total_harvested
    
    def test_direct_total_planted_modification_raises_validation_error(self, test_user):
        """
        Vérifie que la modification directe de total_planted lève ValidationError.
        """
        user, wallet = test_user
        initial_total_planted = wallet.total_planted
        
        wallet.total_planted = 9999
        
        with pytest.raises(ValidationError) as exc_info:
            wallet.save()
        
        error_message = str(exc_info.value)
        assert "VIOLATION CONSTITUTION EGOEJO" in error_message
        assert "total_planted" in error_message
        
        wallet.refresh_from_db()
        assert wallet.total_planted == initial_total_planted
    
    def test_direct_total_composted_modification_raises_validation_error(self, test_user):
        """
        Vérifie que la modification directe de total_composted lève ValidationError.
        """
        user, wallet = test_user
        initial_total_composted = wallet.total_composted
        
        wallet.total_composted = 9999
        
        with pytest.raises(ValidationError) as exc_info:
            wallet.save()
        
        error_message = str(exc_info.value)
        assert "VIOLATION CONSTITUTION EGOEJO" in error_message
        assert "total_composted" in error_message
        
        wallet.refresh_from_db()
        assert wallet.total_composted == initial_total_composted
    
    def test_creation_allowed_without_context(self, db):
        """
        Vérifie que la création initiale (pk None) est autorisée sans contexte.
        """
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        # S'assurer qu'aucun wallet n'existe pour ce user
        SakaWallet.objects.filter(user=user).delete()
        
        # Création initiale doit fonctionner sans AllowSakaMutation
        wallet = SakaWallet(
            user=user,
            balance=100,
            total_harvested=200,
            total_planted=50,
            total_composted=30,
        )
        wallet.save()  # Ne doit pas lever d'erreur
        
        # Vérifier que le wallet a été créé
        assert wallet.pk is not None
        assert wallet.balance == 100
    
    def test_modification_allowed_with_context(self, test_user):
        """
        Vérifie que la modification est autorisée avec AllowSakaMutation().
        
        Les services SAKA doivent pouvoir modifier les champs via ce contexte.
        """
        user, wallet = test_user
        initial_balance = wallet.balance
        
        # Modification avec contexte (simule un service SAKA)
        with AllowSakaMutation():
            wallet.balance = 9999
            wallet.total_harvested = 8888
            wallet.save()  # Ne doit pas lever d'erreur
        
        # Vérifier que la modification a été effectuée
        wallet.refresh_from_db()
        assert wallet.balance == 9999
        assert wallet.total_harvested == 8888
    
    def test_update_raises_validation_error_without_context(self, test_user):
        """
        Vérifie que update() lève ValidationError sans contexte.
        
        Constitution EGOEJO: update() est strictement interdit pour garantir la traçabilité.
        """
        user, wallet = test_user
        initial_balance = wallet.balance
        
        # Tentative de modification via update() sans contexte
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.filter(id=wallet.id).update(balance=9999)
        
        error_message = str(exc_info.value)
        assert "Direct update() is forbidden on SakaWallet" in error_message
        assert "Use SakaTransaction service" in error_message
        
        # Vérifier que le solde n'a pas changé
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance
    
    def test_update_still_raises_error_with_context(self, test_user):
        """
        Vérifie que update() est strictement interdit, même avec AllowSakaMutation().
        
        Constitution EGOEJO: update() est une "porte dérobée" qui doit être fermée.
        AllowSakaMutation() est pour .save(), pas pour .update().
        """
        user, wallet = test_user
        initial_balance = wallet.balance
        
        # Tentative de modification via update() avec contexte (doit quand même échouer)
        with AllowSakaMutation():
            with pytest.raises(ValidationError) as exc_info:
                SakaWallet.objects.filter(id=wallet.id).update(balance=9999)
        
        error_message = str(exc_info.value)
        assert "Direct update() is forbidden on SakaWallet" in error_message
        assert "Use SakaTransaction service" in error_message
        
        # Vérifier que le solde n'a pas changé
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance
    
    def test_bulk_update_raises_validation_error_without_context(self, test_user):
        """
        Vérifie que bulk_update() lève ValidationError sans contexte.
        """
        user, wallet = test_user
        initial_balance = wallet.balance
        
        # Modifier l'objet en mémoire
        wallet.balance = 9999
        
        # Tentative de modification via bulk_update() sans contexte
        with pytest.raises(ValidationError) as exc_info:
            SakaWallet.objects.bulk_update([wallet], ['balance'])
        
        error_message = str(exc_info.value)
        assert "VIOLATION CONSTITUTION EGOEJO" in error_message
        assert "bulk_update()" in error_message
        
        # Vérifier que le solde n'a pas changé
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance
    
    def test_bulk_update_allowed_with_context(self, test_user):
        """
        Vérifie que bulk_update() fonctionne avec AllowSakaMutation().
        """
        user, wallet = test_user
        
        # Modifier l'objet en mémoire
        wallet.balance = 9999
        
        # Modification via bulk_update() avec contexte
        with AllowSakaMutation():
            SakaWallet.objects.bulk_update([wallet], ['balance'])
        
        # Vérifier que la modification a été effectuée
        wallet.refresh_from_db()
        assert wallet.balance == 9999
    
    def test_modification_non_saka_fields_allowed(self, test_user):
        """
        Vérifie que la modification de champs non-SAKA est autorisée sans contexte.
        """
        user, wallet = test_user
        
        # Modification de last_activity_date (champ non-SAKA protégé)
        from django.utils import timezone
        new_date = timezone.now()
        wallet.last_activity_date = new_date
        wallet.save()  # Ne doit pas lever d'erreur
        
        # Vérifier que la modification a été effectuée
        wallet.refresh_from_db()
        assert wallet.last_activity_date == new_date

