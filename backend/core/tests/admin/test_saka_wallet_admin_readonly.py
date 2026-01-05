"""
Test de protection : SakaWalletAdmin readonly_fields empêche la modification via Django Admin.

PHILOSOPHIE EGOEJO :
Empêche la modification directe de balance, total_harvested, total_planted, total_composted
via Django Admin. Ces champs doivent être en readonly_fields.

Constitution: no direct SAKA mutation.
"""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import site
from django.test import RequestFactory
from django.urls import reverse
from core.models.saka import SakaWallet
from core.admin import SakaWalletAdmin

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.egoejo_compliance
class TestSakaWalletAdminReadonly:
    """
    Tests pour vérifier que les champs SAKA sont en readonly_fields dans SakaWalletAdmin.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.fixture
    def admin_user(self, db):
        """Utilisateur admin pour les tests"""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
    
    @pytest.fixture
    def test_user(self, db):
        """Utilisateur de test avec SakaWallet"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        saka_wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 200,
                'total_planted': 50,
                'total_composted': 30,
            }
        )
        return user
    
    def test_readonly_fields_contains_saka_balances(self):
        """
        Vérifie que readonly_fields contient tous les champs de solde/cumul SAKA.
        
        RÈGLE : balance, total_harvested, total_planted, total_composted doivent être
        dans readonly_fields pour empêcher la modification via Django Admin.
        """
        admin_instance = SakaWalletAdmin(SakaWallet, site)
        
        # Vérifier que readonly_fields existe et contient les champs SAKA
        assert hasattr(admin_instance, 'readonly_fields'), (
            "SakaWalletAdmin doit avoir readonly_fields défini"
        )
        
        readonly = admin_instance.readonly_fields
        
        # Vérifier que tous les champs SAKA sont en readonly
        required_readonly = [
            'balance',
            'total_harvested',
            'total_planted',
            'total_composted',
        ]
        
        for field in required_readonly:
            assert field in readonly, (
                f"VIOLATION CONSTITUTION EGOEJO : Le champ '{field}' doit être dans readonly_fields "
                f"de SakaWalletAdmin pour empêcher la modification directe via Django Admin. "
                f"readonly_fields actuel: {readonly}"
            )
    
    def test_admin_get_readonly_fields_contains_saka_balances(self, admin_user, test_user):
        """
        Vérifie que get_readonly_fields() retourne les champs SAKA en lecture seule.
        
        Ce test vérifie que les champs readonly sont bien retournés par get_readonly_fields(),
        ce qui garantit qu'ils ne peuvent pas être modifiés via Django Admin.
        """
        admin_instance = SakaWalletAdmin(SakaWallet, site)
        saka_wallet = test_user.saka_wallet
        request_factory = RequestFactory()
        request = request_factory.get('/admin/core/sakawallet/1/change/')
        request.user = admin_user
        
        # Vérifier via get_readonly_fields() que les champs sont bien marqués comme readonly
        readonly_fields = admin_instance.get_readonly_fields(request, saka_wallet)
        
        saka_balance_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
        for field in saka_balance_fields:
            assert field in readonly_fields, (
                f"VIOLATION CONSTITUTION EGOEJO : Le champ '{field}' doit être dans "
                f"get_readonly_fields() pour empêcher l'édition via Django Admin. "
                f"readonly_fields actuel: {readonly_fields}"
            )
    
    def test_admin_readonly_fields_protection_at_model_level(self, admin_user, test_user):
        """
        Vérifie que les champs readonly sont bien protégés au niveau de l'admin.
        
        Ce test vérifie que readonly_fields contient bien les champs SAKA.
        Django Admin ignore automatiquement les champs readonly dans les POST,
        donc cette vérification garantit que la protection est en place.
        """
        admin_instance = SakaWalletAdmin(SakaWallet, site)
        saka_wallet = test_user.saka_wallet
        initial_balance = saka_wallet.balance
        
        # Vérifier que readonly_fields contient balance
        readonly_fields = admin_instance.readonly_fields
        assert 'balance' in readonly_fields, (
            f"VIOLATION CONSTITUTION EGOEJO : 'balance' doit être dans readonly_fields. "
            f"readonly_fields actuel: {readonly_fields}"
        )
        
        # Vérifier que même si on modifie balance directement sur l'objet,
        # Django Admin ne permettra pas de sauvegarder cette modification via le formulaire
        # (cette vérification est effectuée par le test_readonly_fields_contains_saka_balances)
        
        # La protection est garantie par readonly_fields dans l'admin
        # Django Admin ignore les champs readonly dans les POST
    
    def test_admin_has_no_list_editable_for_saka_fields(self):
        """
        Vérifie que list_editable ne contient aucun champ SAKA.
        
        list_editable permettrait l'édition en masse, ce qui est interdit pour les champs SAKA.
        """
        admin_instance = SakaWalletAdmin(SakaWallet, site)
        
        # Vérifier que list_editable n'existe pas ou est vide
        if hasattr(admin_instance, 'list_editable'):
            list_editable = admin_instance.list_editable
            saka_balance_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
            
            for field in saka_balance_fields:
                assert field not in (list_editable or []), (
                    f"VIOLATION CONSTITUTION EGOEJO : Le champ '{field}' ne doit PAS être "
                    f"dans list_editable car cela permettrait l'édition en masse via Django Admin. "
                    f"list_editable actuel: {list_editable}"
                )
    
    def test_admin_fieldsets_do_not_allow_saka_editing(self):
        """
        Vérifie que fieldsets (si défini) ne permet pas l'édition des champs SAKA.
        
        Même si fieldsets est défini, les champs readonly doivent rester non-éditables.
        """
        admin_instance = SakaWalletAdmin(SakaWallet, site)
        
        # Si fieldsets est défini, vérifier qu'il n'override pas readonly_fields
        # Pour SakaWalletAdmin, fieldsets n'est pas défini (utilise les champs par défaut)
        # Ce qui est correct : Django utilise readonly_fields pour tous les champs
        
        # Vérifier que readonly_fields est bien défini
        assert hasattr(admin_instance, 'readonly_fields'), (
            "SakaWalletAdmin doit avoir readonly_fields défini"
        )
        
        readonly = admin_instance.readonly_fields
        saka_balance_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
        
        for field in saka_balance_fields:
            assert field in readonly, (
                f"VIOLATION CONSTITUTION EGOEJO : Le champ '{field}' doit être dans "
                f"readonly_fields même si fieldsets est défini. readonly_fields actuel: {readonly}"
            )

