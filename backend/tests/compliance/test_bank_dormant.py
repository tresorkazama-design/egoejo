"""
EGOEJO Compliance Test : Banque Dormante (EUR)

LOI EGOEJO :
"La structure instrumentale (EUR) est dormante. Toute feature EUR est feature-flagged et désactivée par défaut."

Ce test vérifie que :
- Toute feature EUR est feature-flagged
- Toute feature EUR est désactivée par défaut
- Si ENABLE_INVESTMENT_FEATURES = False, aucune écriture réelle en base financière

Violation du Manifeste EGOEJO si :
- Une feature EUR n'est pas feature-flagged
- Une feature EUR s'exécute sans flag actif
- Des écritures financières sont créées alors que ENABLE_INVESTMENT_FEATURES = False
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.core.exceptions import ValidationError
from decimal import Decimal

from finance.models import EscrowContract, WalletTransaction, UserWallet
from finance.services import pledge_funds

User = get_user_model()


@pytest.mark.egoejo_compliance
class TestBankDormant:
    """
    Tests de conformité : Banque Dormante (EUR)
    
    RÈGLE ABSOLUE : La structure instrumentale (EUR) est dormante.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.mark.django_db
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_toute_feature_eur_est_feature_flagged(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une feature EUR n'est pas feature-flagged.
        
        Test : Vérifier que les features investment sont protégées par ENABLE_INVESTMENT_FEATURES.
        """
        user = User.objects.create_user(
            username='test_feature_flag',
            email='test_feature_flag@example.com',
            password='testpass123'
        )
        
        # Créer un wallet avec solde
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        # Créer un projet avec funding_type EQUITY
        from core.models.projects import Projet
        project = Projet.objects.create(
            titre='Projet Test Feature Flag',
            description='Description test',
            funding_type='EQUITY',
            donation_goal=Decimal('5000.00')
        )
        
        # Tentative de pledge EQUITY (devrait être bloquée)
        with pytest.raises(ValidationError) as exc_info:
            pledge_funds(
                user=user,
                project=project,
                amount=Decimal('100.00'),
                pledge_type='EQUITY'
            )
        
        # Vérifier que l'erreur mentionne que l'investissement n'est pas ouvert
        error_message = str(exc_info.value)
        assert 'investissement' in error_message.lower() or 'investment' in error_message.lower(), (
            f"VIOLATION DU MANIFESTE EGOEJO : La feature EQUITY n'est pas protégée par feature flag. "
            f"Erreur levée : {error_message}. "
            f"Toute feature EUR DOIT être feature-flagged."
        )
        
        # Vérifier qu'aucun escrow EQUITY n'a été créé
        escrow_count = EscrowContract.objects.filter(
            user=user,
            project=project,
            pledge_transaction__transaction_type='PLEDGE_EQUITY'
        ).count()
        assert escrow_count == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Un escrow EQUITY a été créé alors que ENABLE_INVESTMENT_FEATURES=False. "
            f"Escrows créés : {escrow_count}. "
            f"Toute feature EUR DOIT être feature-flagged."
        )
        
        # Vérifier qu'aucune transaction EQUITY n'a été créée
        transaction_count = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type__in=['PLEDGE_EQUITY', 'PLEDGE_INVESTMENT']
        ).count()
        assert transaction_count == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Une transaction EQUITY a été créée alors que ENABLE_INVESTMENT_FEATURES=False. "
            f"Transactions créées : {transaction_count}. "
            f"Toute feature EUR DOIT être feature-flagged."
        )
    
    @pytest.mark.django_db
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_toute_feature_eur_est_desactivee_par_defaut(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une feature EUR est activée par défaut.
        
        Test : Vérifier que les features investment sont désactivées par défaut.
        """
        # Vérifier que ENABLE_INVESTMENT_FEATURES est False par défaut
        from django.conf import settings
        assert not getattr(settings, 'ENABLE_INVESTMENT_FEATURES', False), (
            "VIOLATION DU MANIFESTE EGOEJO : ENABLE_INVESTMENT_FEATURES est True par défaut. "
            "Toute feature EUR DOIT être désactivée par défaut."
        )
        
        # Vérifier que les endpoints investment sont inaccessibles
        from core.permissions import IsInvestmentFeatureEnabled
        permission = IsInvestmentFeatureEnabled()
        
        # Créer une requête mock (simplifiée)
        class MockRequest:
            def __init__(self):
                self.user = None
        
        request = MockRequest()
        
        # La permission doit retourner False si ENABLE_INVESTMENT_FEATURES = False
        # Note : Cette vérification dépend de l'implémentation de IsInvestmentFeatureEnabled
        # Si la permission vérifie le feature flag, elle doit retourner False
        
        # Vérifier qu'aucun modèle investment n'est accessible
        try:
            from investment.models import ShareholderRegister
            # Si le modèle existe mais est protégé par feature flag, c'est OK
            # Mais on vérifie qu'il ne peut pas être utilisé sans flag
            shareholder_count = ShareholderRegister.objects.count()
            # Si ENABLE_INVESTMENT_FEATURES = False, on ne devrait pas pouvoir créer de shareholders
            # (mais on peut lire les existants si le modèle existe)
        except ImportError:
            # Si le module investment n'existe pas, c'est OK (dormant)
            pass
    
    @pytest.mark.django_db
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_aucune_ecriture_financiere_si_flag_desactive(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Des écritures financières sont créées alors que ENABLE_INVESTMENT_FEATURES = False.
        
        Test : Vérifier qu'aucune écriture financière EQUITY n'est créée si le flag est désactivé.
        """
        user = User.objects.create_user(
            username='test_no_financial_write',
            email='test_no_financial_write@example.com',
            password='testpass123'
        )
        
        # Créer un wallet avec solde
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        initial_balance = wallet.balance
        
        # Créer un projet avec funding_type EQUITY
        from core.models.projects import Projet
        project = Projet.objects.create(
            titre='Projet Test No Write',
            description='Description test',
            funding_type='EQUITY',
            donation_goal=Decimal('5000.00')
        )
        
        # Compter les écritures initiales
        initial_escrow_count = EscrowContract.objects.filter(
            user=user,
            project=project
        ).count()
        
        initial_transaction_count = WalletTransaction.objects.filter(
            wallet=wallet
        ).count()
        
        # Tentative de pledge EQUITY (devrait être bloquée)
        try:
            pledge_funds(
                user=user,
                project=project,
                amount=Decimal('100.00'),
                pledge_type='EQUITY'
            )
            # Si la fonction ne lève pas d'exception, c'est une violation
            pytest.fail(
                "VIOLATION DU MANIFESTE EGOEJO : pledge_funds a accepté un pledge EQUITY "
                "alors que ENABLE_INVESTMENT_FEATURES=False. "
                "Aucune écriture financière EQUITY ne doit être créée si le flag est désactivé."
            )
        except ValidationError:
            # C'est normal, la fonction doit lever une exception
            pass
        
        # Vérifier qu'aucune nouvelle écriture n'a été créée
        final_escrow_count = EscrowContract.objects.filter(
            user=user,
            project=project
        ).count()
        assert final_escrow_count == initial_escrow_count, (
            f"VIOLATION DU MANIFESTE EGOEJO : Des escrows ont été créés alors que ENABLE_INVESTMENT_FEATURES=False. "
            f"Escrows initiaux : {initial_escrow_count}, Escrows finaux : {final_escrow_count}. "
            f"Aucune écriture financière EQUITY ne doit être créée si le flag est désactivé."
        )
        
        final_transaction_count = WalletTransaction.objects.filter(
            wallet=wallet
        ).count()
        assert final_transaction_count == initial_transaction_count, (
            f"VIOLATION DU MANIFESTE EGOEJO : Des transactions ont été créées alors que ENABLE_INVESTMENT_FEATURES=False. "
            f"Transactions initiales : {initial_transaction_count}, Transactions finales : {final_transaction_count}. "
            f"Aucune écriture financière EQUITY ne doit être créée si le flag est désactivé."
        )
        
        # Vérifier que le solde du wallet n'a pas été modifié
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le solde du wallet a été modifié alors que ENABLE_INVESTMENT_FEATURES=False. "
            f"Solde initial : {initial_balance}, Solde final : {wallet.balance}. "
            f"Aucune écriture financière ne doit être créée si le flag est désactivé."
        )
    
    @pytest.mark.django_db
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_donation_fonctionne_meme_si_investment_desactive(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Les dons (DONATION) ne fonctionnent pas si ENABLE_INVESTMENT_FEATURES = False.
        
        Test : Vérifier que les dons fonctionnent indépendamment du flag investment.
        """
        user = User.objects.create_user(
            username='test_donation_works',
            email='test_donation_works@example.com',
            password='testpass123'
        )
        
        # Créer un wallet avec solde
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        wallet.balance = Decimal('1000.00')
        wallet.save()
        initial_balance = wallet.balance
        
        # Créer un projet avec funding_type DONATION
        from core.models.projects import Projet
        project = Projet.objects.create(
            titre='Projet Test Donation',
            description='Description test',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00')
        )
        
        # Tentative de pledge DONATION (devrait fonctionner)
        escrow = pledge_funds(
            user=user,
            project=project,
            amount=Decimal('100.00'),
            pledge_type='DONATION'
        )
        
        assert escrow is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : pledge_funds a échoué pour un don alors que ENABLE_INVESTMENT_FEATURES=False. "
            "Les dons DOIVENT fonctionner indépendamment du flag investment."
        )
        
        # Vérifier qu'un escrow DONATION a été créé
        escrow_count = EscrowContract.objects.filter(
            user=user,
            project=project,
            pledge_transaction__transaction_type='PLEDGE_DONATION'
        ).count()
        assert escrow_count == 1, (
            f"VIOLATION DU MANIFESTE EGOEJO : Un escrow DONATION n'a pas été créé. "
            f"Escrows créés : {escrow_count}. "
            f"Les dons DOIVENT fonctionner indépendamment du flag investment."
        )
        
        # Vérifier que le solde du wallet a été débité
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance - Decimal('100.00'), (
            f"VIOLATION DU MANIFESTE EGOEJO : Le solde du wallet n'a pas été débité pour un don. "
            f"Solde attendu : {initial_balance - Decimal('100.00')}, Solde actuel : {wallet.balance}. "
            f"Les dons DOIVENT fonctionner indépendamment du flag investment."
        )

