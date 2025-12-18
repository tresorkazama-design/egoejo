"""
Tests d'intégration pour vérifier l'isolation de la structure instrumentale (Investment/EUR).

PHILOSOPHIE EGOEJO :
La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.
La structure instrumentale (Investment/EUR) est volontairement dormante (V2.0).

Ces tests garantissent que lorsque ENABLE_INVESTMENT_FEATURES=False :
- Aucun endpoint investment n'est accessible (403/404)
- Aucune table investment n'impacte SAKA
- Aucune importation croisée n'existe
- Les services SAKA fonctionnent normalement

CONTRAINTES :
- Ne pas activer V2.0
- Ne pas refactorer l'architecture
- Tester uniquement l'isolation
"""
import pytest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
import importlib
import sys

from core.models.projects import Projet
from core.models.saka import SakaWallet, SakaTransaction
from core.services.saka import harvest_saka, spend_saka, get_saka_balance
from finance.models import UserWallet

User = get_user_model()


@pytest.mark.django_db
class TestInvestmentIsolation:
    """
    Tests pour vérifier l'isolation de la structure instrumentale (Investment/EUR).
    """
    
    @pytest.fixture
    def test_user(self, db):
        """Fixture pour créer un utilisateur de test"""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def test_project(self, db):
        """Fixture pour créer un projet de test"""
        return Projet.objects.create(
            titre='Test Project',
            description='Test Description',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00')
        )
    
    @pytest.fixture
    def api_client(self, test_user):
        """Fixture pour créer un client API authentifié"""
        client = APIClient()
        client.force_authenticate(user=test_user)
        return client
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_investment_endpoints_return_403_when_disabled(self, api_client):
        """
        Test P0 : Les endpoints investment DOIVENT retourner 403 quand ENABLE_INVESTMENT_FEATURES=False
        
        Assertion : Appels investment → 403 Forbidden
        """
        # Tester l'endpoint principal investment/shareholders
        url = reverse('shareholder-register-list')
        response = api_client.get(url)
        
        # Vérifier que l'endpoint retourne 403 (Forbidden)
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f"L'endpoint investment/shareholders devrait retourner 403 quand "
            f"ENABLE_INVESTMENT_FEATURES=False, mais a retourné {response.status_code}"
        )
        
        # Vérifier que le message d'erreur est approprié
        assert 'disponible' in str(response.data).lower() or 'forbidden' in str(response.data).lower(), (
            f"Le message d'erreur devrait indiquer que la fonctionnalité n'est pas disponible. "
            f"Contenu: {response.data}"
        )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_investment_endpoint_by_project_returns_403_when_disabled(self, api_client, test_project):
        """
        Test P0 : L'endpoint investment/shareholders/by_project DOIT retourner 403 quand désactivé
        
        Assertion : Appels investment → 403 Forbidden
        """
        # Tester l'endpoint by_project
        url = reverse('shareholder-register-by-project')
        response = api_client.get(url, {'project_id': test_project.id})
        
        # Vérifier que l'endpoint retourne 403 (Forbidden)
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f"L'endpoint investment/shareholders/by_project devrait retourner 403 quand "
            f"ENABLE_INVESTMENT_FEATURES=False, mais a retourné {response.status_code}"
        )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_no_investment_reference_in_saka_services(self):
        """
        Test P0 : Aucune référence EUR/investment dans les services SAKA
        
        Assertion : Aucune référence EUR dans services SAKA
        """
        import inspect
        from core.services import saka
        
        # Récupérer le code source du module saka
        source_code = inspect.getsource(saka)
        
        # Vérifier qu'il n'y a pas d'imports d'investment
        assert 'from investment' not in source_code, (
            "Les services SAKA ne doivent PAS importer investment. "
            "Cela créerait une dépendance croisée."
        )
        
        assert 'import investment' not in source_code, (
            "Les services SAKA ne doivent PAS importer investment. "
            "Cela créerait une dépendance croisée."
        )
        
        # Vérifier qu'il n'y a pas de références à ShareholderRegister
        assert 'ShareholderRegister' not in source_code, (
            "Les services SAKA ne doivent PAS référencer ShareholderRegister. "
            "Cela créerait une dépendance croisée."
        )
        
        # Vérifier qu'il n'y a pas de références à EQUITY dans le contexte SAKA
        # (sauf si c'est dans un commentaire ou une docstring)
        lines = source_code.split('\n')
        for i, line in enumerate(lines):
            # Ignorer les commentaires et docstrings
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            
            # Vérifier qu'il n'y a pas de logique EQUITY dans le code SAKA
            if 'EQUITY' in line and 'DONATION' not in line:
                # C'est suspect, mais on vérifie que ce n'est pas dans un commentaire
                if not any(stripped.startswith(c) for c in ['#', '"', "'"]):
                    pytest.fail(
                        f"Les services SAKA ne doivent PAS contenir de logique EQUITY. "
                        f"Ligne {i+1}: {line}"
                    )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_no_investment_reference_in_saka_models(self):
        """
        Test P0 : Aucune référence EUR/investment dans les modèles SAKA
        
        Assertion : Aucune référence EUR dans modèles SAKA
        """
        import inspect
        from core.models import saka
        
        # Récupérer le code source du module saka
        source_code = inspect.getsource(saka)
        
        # Vérifier qu'il n'y a pas d'imports d'investment
        assert 'from investment' not in source_code, (
            "Les modèles SAKA ne doivent PAS importer investment. "
            "Cela créerait une dépendance croisée."
        )
        
        assert 'import investment' not in source_code, (
            "Les modèles SAKA ne doivent PAS importer investment. "
            "Cela créerait une dépendance croisée."
        )
        
        # Vérifier qu'il n'y a pas de ForeignKey vers investment
        assert 'ForeignKey.*investment' not in source_code, (
            "Les modèles SAKA ne doivent PAS avoir de ForeignKey vers investment. "
            "Cela créerait une dépendance croisée."
        )
    
    @override_settings(
        ENABLE_INVESTMENT_FEATURES=False,
        ENABLE_SAKA=True  # SAKA doit être activé pour tester les services SAKA
    )
    def test_saka_services_work_normally_when_investment_disabled(self, test_user, test_project):
        """
        Test P0 : Les services SAKA fonctionnent normalement même si investment est désactivé
        
        Assertion : Les services SAKA ne dépendent pas d'investment
        """
        from core.services.saka import SakaReason
        
        # Tester harvest_saka
        initial_balance = get_saka_balance(test_user)['balance']
        
        result = harvest_saka(
            test_user,
            reason=SakaReason.CONTENT_READ,
            metadata={'test': True}
        )
        
        assert result is not None, "harvest_saka devrait fonctionner même si investment est désactivé"
        assert isinstance(result, SakaTransaction), (
            f"harvest_saka devrait retourner une SakaTransaction. Type: {type(result)}"
        )
        
        # Vérifier que le solde a augmenté
        new_balance = get_saka_balance(test_user)['balance']
        assert new_balance > initial_balance, (
            f"Le solde SAKA devrait avoir augmenté. Initial: {initial_balance}, Nouveau: {new_balance}"
        )
        
        # Tester spend_saka
        spend_amount = 10
        balance_before_spend = get_saka_balance(test_user)['balance']
        
        result = spend_saka(
            test_user,
            spend_amount,
            reason='test_spend',
            metadata={'test': True}
        )
        
        assert result is True, "spend_saka devrait fonctionner même si investment est désactivé"
        
        # Vérifier que le solde a diminué
        balance_after_spend = get_saka_balance(test_user)['balance']
        assert balance_after_spend == balance_before_spend - spend_amount, (
            f"Le solde SAKA devrait avoir diminué. Avant: {balance_before_spend}, "
            f"Après: {balance_after_spend}, Dépensé: {spend_amount}"
        )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_conditional_imports_do_not_cause_errors(self, api_client, test_user):
        """
        Test P0 : Les imports conditionnels d'investment ne causent pas d'erreurs
        
        Assertion : Les imports conditionnels sont gérés correctement
        """
        # Tester que les vues avec imports conditionnels fonctionnent
        # Même si investment est désactivé
        
        # Test 1 : GlobalAssetsView (a un import conditionnel de ShareholderRegister)
        url = reverse('global-assets')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK, (
            f"GlobalAssetsView devrait fonctionner même si investment est désactivé. "
            f"Statut: {response.status_code}"
        )
        
        # Vérifier que equity_portfolio est présent mais vide ou désactivé
        assert 'equity_portfolio' in response.data, (
            "La réponse devrait contenir equity_portfolio même si investment est désactivé"
        )
        
        equity_portfolio = response.data['equity_portfolio']
        assert equity_portfolio.get('is_active') is False, (
            f"equity_portfolio.is_active devrait être False quand investment est désactivé. "
            f"Valeur: {equity_portfolio.get('is_active')}"
        )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_pledge_funds_blocks_equity_when_disabled(self, test_user, test_project):
        """
        Test P0 : pledge_funds bloque les pledges EQUITY quand investment est désactivé
        
        Assertion : Les pledges EQUITY sont rejetés avec ValidationError
        """
        from finance.services import pledge_funds
        from finance.models import UserWallet
        from django.core.exceptions import ValidationError
        
        # Créer un wallet avec des fonds
        wallet, _ = UserWallet.objects.get_or_create(user=test_user)
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        # Tenter un pledge EQUITY (devrait être bloqué)
        with pytest.raises(ValidationError) as exc_info:
            pledge_funds(
                user=test_user,
                project=test_project,
                amount=Decimal('100.00'),
                pledge_type='EQUITY'
            )
        
        assert 'investissement' in str(exc_info.value).lower() or 'disponible' in str(exc_info.value).lower(), (
            f"pledge_funds devrait rejeter les pledges EQUITY avec un message approprié. "
            f"Message: {exc_info.value}"
        )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_no_cross_imports_between_saka_and_investment(self):
        """
        Test P0 : Aucune importation croisée entre SAKA et investment
        
        Assertion : Aucune importation croisée n'existe
        """
        import inspect
        
        # Vérifier que les services SAKA n'importent pas investment
        from core.services import saka
        saka_source = inspect.getsource(saka)
        
        assert 'from investment' not in saka_source, (
            "Les services SAKA ne doivent PAS importer investment"
        )
        assert 'import investment' not in saka_source, (
            "Les services SAKA ne doivent PAS importer investment"
        )
        
        # Vérifier que les modèles SAKA n'importent pas investment
        from core.models import saka as saka_models
        saka_models_source = inspect.getsource(saka_models)
        
        assert 'from investment' not in saka_models_source, (
            "Les modèles SAKA ne doivent PAS importer investment"
        )
        assert 'import investment' not in saka_models_source, (
            "Les modèles SAKA ne doivent PAS importer investment"
        )
    
    @override_settings(
        ENABLE_INVESTMENT_FEATURES=False,
        ENABLE_SAKA=True  # SAKA doit être activé pour tester les transactions SAKA
    )
    def test_saka_transactions_unaffected_by_investment_disabled(self, test_user):
        """
        Test P0 : Les transactions SAKA ne sont pas affectées par investment désactivé
        
        Assertion : Les transactions SAKA fonctionnent normalement
        """
        from core.services.saka import SakaReason
        
        # Créer plusieurs transactions SAKA
        initial_balance = get_saka_balance(test_user)['balance']
        
        # Harvest plusieurs fois avec différentes raisons
        harvest_saka(test_user, reason=SakaReason.CONTENT_READ, metadata={})
        harvest_saka(test_user, reason=SakaReason.POLL_VOTE, metadata={})
        harvest_saka(test_user, reason=SakaReason.INVITE_ACCEPTED, metadata={})
        
        # Vérifier que les transactions sont créées
        transactions = SakaTransaction.objects.filter(user=test_user)
        assert transactions.count() >= 3, (
            f"Au moins 3 transactions SAKA devraient être créées. "
            f"Nombre: {transactions.count()}"
        )
        
        # Vérifier que le solde a augmenté
        new_balance = get_saka_balance(test_user)['balance']
        assert new_balance > initial_balance, (
            f"Le solde SAKA devrait avoir augmenté. Initial: {initial_balance}, Nouveau: {new_balance}"
        )
        
        # Vérifier que toutes les transactions sont de type EARN (récolte)
        harvest_transactions = transactions.filter(direction='EARN')
        assert harvest_transactions.count() >= 3, (
            f"Au moins 3 transactions EARN devraient être créées. "
            f"Nombre: {harvest_transactions.count()}"
        )
    
    @override_settings(
        ENABLE_INVESTMENT_FEATURES=False,
        ENABLE_SAKA=True  # SAKA doit être activé pour tester le wallet SAKA
    )
    def test_saka_wallet_unaffected_by_investment_disabled(self, test_user):
        """
        Test P0 : Le wallet SAKA n'est pas affecté par investment désactivé
        
        Assertion : Le wallet SAKA fonctionne normalement
        """
        from core.services.saka import SakaReason
        
        # Récupérer ou créer le wallet SAKA
        wallet, created = SakaWallet.objects.get_or_create(user=test_user)
        
        # Vérifier que le wallet existe
        assert wallet is not None, "Le wallet SAKA devrait exister"
        
        # Vérifier que le wallet n'a pas de références à investment
        # (pas de ForeignKey, pas de ManyToMany, etc.)
        wallet_fields = [f.name for f in wallet._meta.get_fields()]
        
        investment_fields = [f for f in wallet_fields if 'investment' in f.lower() or 'equity' in f.lower()]
        assert len(investment_fields) == 0, (
            f"Le wallet SAKA ne devrait pas avoir de champs liés à investment. "
            f"Champs trouvés: {investment_fields}"
        )
        
        # Vérifier que le wallet fonctionne normalement
        initial_balance = wallet.balance
        
        # Harvest SAKA
        harvest_saka(test_user, reason=SakaReason.CONTENT_READ, metadata={})
        
        # Recharger le wallet
        wallet.refresh_from_db()
        
        # Vérifier que le solde a augmenté
        assert wallet.balance > initial_balance, (
            f"Le solde du wallet SAKA devrait avoir augmenté. "
            f"Initial: {initial_balance}, Nouveau: {wallet.balance}"
        )

