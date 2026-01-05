"""
Tests de conformité : Vérification que la banque dormante (EUR) reste strictement dormante

PHILOSOPHIE EGOEJO :
- La structure instrumentale (EUR) est DORMANTE
- Elle ne doit JAMAIS contraindre la structure relationnelle (SAKA)
- Chaque accès financier DOIT être derrière un feature flag
- Aucune feature financière ne doit s'exécuter sans flag actif
- Aucune feature financière ne doit impacter SAKA

Ces tests analysent le code réel pour détecter toute violation.
"""
import re
import ast
import inspect
from pathlib import Path
import pytest
from django.test import override_settings
from django.conf import settings


@pytest.mark.egoejo_compliance
class TestBanqueDormanteStrict:
    """
    Tests de conformité : Vérification que la banque dormante (EUR) reste strictement dormante
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.fixture
    def finance_service_path(self):
        """Chemin vers le service Finance"""
        return Path(__file__).parent.parent.parent / "finance" / "services.py"
    
    @pytest.fixture
    def investment_views_path(self):
        """Chemin vers les vues Investment"""
        investment_path = Path(__file__).parent.parent.parent / "investment" / "views.py"
        if investment_path.exists():
            return investment_path
        return None
    
    @pytest.fixture
    def finance_views_path(self):
        """Chemin vers les vues Finance"""
        return Path(__file__).parent.parent.parent / "finance" / "views.py"
    
    def test_tous_acces_investment_proteges_par_feature_flag(self, investment_views_path):
        """
        Vérifie que TOUS les accès aux features investment sont protégés par ENABLE_INVESTMENT_FEATURES.
        
        RÈGLE ABSOLUE : La structure instrumentale (Investment/EUR) ne doit jamais s'exécuter sans flag actif.
        """
        if investment_views_path is None or not investment_views_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le module Investment est introuvable ou non activé. "
                f"Chemin attendu : {investment_views_path}. "
                f"Ce module est OBLIGATOIRE pour la conformité EGOEJO (même s'il est dormant). "
                f"Sans ce module, les protections contre l'activation non contrôlée des features investment ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(investment_views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que le fichier utilise un décorateur ou une permission qui vérifie le flag
        # Les vues investment utilisent généralement un décorateur ou une permission
        violations = []
        
        # Vérifier la présence d'un décorateur ou permission qui vérifie le flag
        # Pattern 1 : Décorateur @require_investment_features ou similaire
        # Pattern 2 : Permission IsInvestmentEnabled
        # Pattern 3 : Vérification directe dans la vue
        
        has_global_protection = any(pattern in content for pattern in [
            'ENABLE_INVESTMENT_FEATURES',
            'IsInvestmentEnabled',
            'require_investment',
            '@require_investment',
        ])
        
        # Si le fichier contient des vues mais pas de protection globale, vérifier chaque vue
        if not has_global_protection:
            # Chercher les définitions de vues
            view_patterns = [
                r'def\s+(\w+)\s*\(.*request',
                r'class\s+(\w+View)\s*\(',
            ]
            
            for pattern in view_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    view_name = match.group(1)
                    start_pos = match.start()
                    
                    # Extraire le corps de la vue (premières 30 lignes)
                    lines = content[start_pos:start_pos+800].split('\n')
                    view_body = '\n'.join(lines[:30])
                    
                    # Vérifier si la vue utilise des features investment
                    uses_investment = any(keyword in view_body.lower() for keyword in [
                        'shareholder', 'equity', 'investment'
                    ])
                    
                    if uses_investment:
                        # Vérifier si le feature flag est vérifié dans la vue
                        has_flag_check = any(check in view_body for check in [
                            'ENABLE_INVESTMENT_FEATURES',
                            'getattr(settings, "ENABLE_INVESTMENT_FEATURES"',
                            'settings.ENABLE_INVESTMENT_FEATURES',
                            'IsInvestmentEnabled',
                            '@require_investment',
                        ])
                        
                        if not has_flag_check:
                            line_num = content[:start_pos].count('\n') + 1
                            violations.append(f"Ligne {line_num}: {view_name} utilise investment sans vérifier ENABLE_INVESTMENT_FEATURES")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Accès investment sans feature flag dans {investment_views_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Tous les accès investment DOIVENT être protégés par ENABLE_INVESTMENT_FEATURES."
        )
    
    def test_aucune_feature_financiere_impacte_saka(self):
        """
        Vérifie qu'aucune feature financière (EUR) n'impacte SAKA.
        
        RÈGLE ABSOLUE : La structure instrumentale ne doit JAMAIS contraindre la structure relationnelle.
        """
        # Scanner les services finance pour vérifier qu'ils n'importent pas SAKA
        finance_service_path = Path(__file__).parent.parent.parent / "finance" / "services.py"
        
        if not finance_service_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'finance/services.py' est introuvable. "
                f"Chemin attendu : {finance_service_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre l'impact Finance/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(finance_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : références SAKA dans services finance
        forbidden_patterns = [
            r'from.*saka.*import',
            r'import.*saka',
            r'SakaWallet|SakaTransaction|SakaSilo',
            r'harvest_saka|spend_saka',
            r'saka_wallet|saka_transaction',
            r'saka.*balance|balance.*saka',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Feature financière impacte SAKA dans {finance_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : La structure instrumentale (EUR) ne doit JAMAIS contraindre SAKA."
        )
    
    def test_escrow_ne_impacte_pas_saka(self):
        """
        Vérifie que les opérations escrow n'impactent pas SAKA.
        
        RÈGLE ABSOLUE : Les escrows (EUR) et SAKA sont strictement séparés.
        """
        finance_service_path = Path(__file__).parent.parent.parent / "finance" / "services.py"
        
        if not finance_service_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'finance/services.py' est introuvable. "
                f"Chemin attendu : {finance_service_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre l'impact Finance/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(finance_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que les fonctions escrow (pledge_funds, release_escrow) ne référencent pas SAKA
        escrow_functions = ['pledge_funds', 'release_escrow', 'refund_escrow']
        
        violations = []
        for func_name in escrow_functions:
            # Chercher la définition de la fonction
            func_pattern = rf'def\s+{func_name}\s*\([^)]*\):'
            match = re.search(func_pattern, content, re.MULTILINE)
            
            if match:
                # Extraire le corps de la fonction (jusqu'à la prochaine fonction ou fin)
                func_start = match.end()
                func_body = content[func_start:func_start+1000]  # 1000 caractères après la définition
                
                # Vérifier qu'il n'y a pas de référence SAKA
                saka_patterns = [
                    r'saka',
                    r'SakaWallet',
                    r'SakaTransaction',
                    r'harvest_saka|spend_saka',
                ]
                
                for saka_pattern in saka_patterns:
                    if re.search(saka_pattern, func_body, re.IGNORECASE):
                        line_num = content[:func_start].count('\n') + 1
                        violations.append(f"Fonction {func_name} : Référence SAKA détectée (ligne ~{line_num})")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Opérations escrow impactent SAKA dans {finance_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Les escrows (EUR) et SAKA sont strictement séparés."
        )
    
    def test_aucune_feature_financiere_sans_flag_actif(self):
        """
        Vérifie qu'aucune feature financière ne s'exécute sans flag actif.
        
        RÈGLE ABSOLUE : La structure instrumentale (EUR) est DORMANTE par défaut.
        """
        finance_views_path = Path(__file__).parent.parent.parent / "finance" / "views.py"
        
        if not finance_views_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'finance/views.py' est introuvable. "
                f"Chemin attendu : {finance_views_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre l'activation non contrôlée des features financières ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(finance_views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que les endpoints finance vérifient le feature flag si nécessaire
        # (Les endpoints finance de base peuvent être actifs, mais pas investment)
        # On se concentre sur les endpoints qui utilisent des features avancées
        
        violations = []
        
        # Chercher les définitions de vues
        view_patterns = [
            r'def\s+(\w+)\s*\(.*request',
            r'class\s+(\w+View)\s*\(',
        ]
        
        for pattern in view_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                view_name = match.group(1)
                start_pos = match.start()
                
                # Extraire le corps de la vue
                view_body = content[start_pos:start_pos+300]
                
                # Vérifier si la vue utilise des features investment
                uses_investment = any(keyword in view_body.lower() for keyword in [
                    'equity', 'shareholder', 'investment'
                ])
                
                if uses_investment:
                    # Vérifier si le feature flag est vérifié
                    has_flag_check = any(check in view_body for check in [
                        'ENABLE_INVESTMENT_FEATURES',
                        'getattr(settings, "ENABLE_INVESTMENT_FEATURES"',
                        'settings.ENABLE_INVESTMENT_FEATURES',
                    ])
                    
                    if not has_flag_check:
                        line_num = content[:start_pos].count('\n') + 1
                        violations.append(f"Ligne {line_num}: {view_name} utilise investment sans vérifier ENABLE_INVESTMENT_FEATURES")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Feature financière s'exécute sans flag actif dans {finance_views_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Toutes les features investment DOIVENT vérifier ENABLE_INVESTMENT_FEATURES."
        )
    
    @pytest.mark.django_db
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_pledge_funds_bloque_equity_si_flag_desactive(self):
        """
        Vérifie que pledge_funds bloque les pledges EQUITY si ENABLE_INVESTMENT_FEATURES=False.
        
        RÈGLE ABSOLUE : La structure instrumentale (Investment/EUR) ne doit pas s'exécuter sans flag actif.
        """
        from django.contrib.auth import get_user_model
        from finance.services import pledge_funds
        from finance.models import EscrowContract, WalletTransaction
        from core.models.projects import Projet
        from decimal import Decimal
        from django.core.exceptions import ValidationError
        
        User = get_user_model()
        
        user = User.objects.create_user(
            username='test_finance',
            email='test_finance@example.com',
            password='testpass123'
        )
        
        project = Projet.objects.create(
            titre='Projet Test Finance',
            description='Description test',
            funding_type='EQUITY',
            donation_goal=Decimal('1000.00')
        )
        
        # Créer un wallet avec solde
        from finance.models import UserWallet
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        wallet.balance = Decimal('500.00')
        wallet.save()
        
        # Tenter un pledge EQUITY (doit être bloqué)
        with pytest.raises(ValidationError) as exc_info:
            pledge_funds(
                user=user,
                project=project,
                amount=Decimal('100.00'),
                pledge_type='EQUITY'
            )
        
        assert "L'investissement n'est pas encore ouvert" in str(exc_info.value) or \
               "investissement" in str(exc_info.value).lower(), (
            f"VIOLATION CONSTITUTION EGOEJO : pledge_funds a accepté un pledge EQUITY alors que ENABLE_INVESTMENT_FEATURES=False.\n"
            f"Erreur levée : {exc_info.value}\n\n"
            f"ACTION REQUISE : pledge_funds DOIT bloquer EQUITY si ENABLE_INVESTMENT_FEATURES=False."
        )
        
        # Vérifier qu'aucun escrow n'a été créé
        escrow_count = EscrowContract.objects.filter(user=user, project=project).count()
        assert escrow_count == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Un escrow EQUITY a été créé alors que ENABLE_INVESTMENT_FEATURES=False.\n"
            f"Escrows créés : {escrow_count}\n\n"
            f"ACTION REQUISE : Aucun escrow EQUITY ne doit être créé si le flag est désactivé."
        )
        
        # Vérifier qu'aucune transaction n'a été créée
        transaction_count = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type__in=['PLEDGE_EQUITY', 'PLEDGE_INVESTMENT']
        ).count()
        assert transaction_count == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Une transaction EQUITY a été créée alors que ENABLE_INVESTMENT_FEATURES=False.\n"
            f"Transactions créées : {transaction_count}\n\n"
            f"ACTION REQUISE : Aucune transaction EQUITY ne doit être créée si le flag est désactivé."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_INVESTMENT_FEATURES=False,
        ENABLE_SAKA=True,  # SAKA doit être activé pour fonctionner
    )
    def test_saka_non_impacte_par_finance_desactivee(self):
        """
        Vérifie que SAKA n'est pas impacté par la désactivation des features finance.
        
        RÈGLE ABSOLUE : La structure relationnelle (SAKA) est PRIORITAIRE et indépendante.
        """
        from django.contrib.auth import get_user_model
        from core.services.saka import harvest_saka, spend_saka, SakaReason
        from core.models.saka import SakaWallet, SakaTransaction
        
        User = get_user_model()
        
        user = User.objects.create_user(
            username='test_saka_independent',
            email='test_saka_independent@example.com',
            password='testpass123'
        )
        
        # Vérifier que SAKA fonctionne normalement même si investment est désactivé
        initial_balance = 0
        
        # Récolter du SAKA
        harvest_result = harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        assert harvest_result is not None, (
            "VIOLATION CONSTITUTION EGOEJO : harvest_saka a échoué alors que investment est désactivé.\n"
            "SAKA DOIT fonctionner indépendamment de la structure instrumentale (EUR)."
        )
        
        wallet = user.saka_wallet
        wallet.refresh_from_db()
        assert wallet.balance == 100, (
            f"VIOLATION CONSTITUTION EGOEJO : Le solde SAKA n'a pas été crédité.\n"
            f"Solde attendu : 100, Solde actuel : {wallet.balance}\n\n"
            f"ACTION REQUISE : SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
        
        # Dépenser du SAKA
        spend_result = spend_saka(user, 30, "test_spend")
        assert spend_result is True, (
            "VIOLATION CONSTITUTION EGOEJO : spend_saka a échoué alors que investment est désactivé.\n"
            "SAKA DOIT fonctionner indépendamment de la structure instrumentale (EUR)."
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == 70, (
            f"VIOLATION CONSTITUTION EGOEJO : Le solde SAKA n'a pas été débité.\n"
            f"Solde attendu : 70, Solde actuel : {wallet.balance}\n\n"
            f"ACTION REQUISE : SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
        
        # Vérifier que les transactions SAKA ont été créées
        transaction_count = SakaTransaction.objects.filter(user=user).count()
        assert transaction_count >= 2, (
            f"VIOLATION CONSTITUTION EGOEJO : Les transactions SAKA n'ont pas été créées.\n"
            f"Transactions attendues : >= 2, Transactions créées : {transaction_count}\n\n"
            f"ACTION REQUISE : Les transactions SAKA DOIVENT être créées indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
    
    def test_structure_instrumentale_ne_contraint_pas_relationnelle(self):
        """
        Vérifie que la structure instrumentale (EUR) ne contraint jamais la structure relationnelle (SAKA).
        
        RÈGLE ABSOLUE : La structure relationnelle (SAKA) est PRIORITAIRE.
        La structure instrumentale (EUR) ne doit JAMAIS contraindre SAKA.
        """
        # Scanner tous les fichiers SAKA pour vérifier qu'ils n'ont pas de dépendances conditionnelles sur EUR
        saka_service_path = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        
        if not saka_service_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'core/services/saka.py' est introuvable. "
                f"Chemin attendu : {saka_service_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la contrainte EUR/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(saka_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : contraintes conditionnelles sur EUR
        forbidden_patterns = [
            r'if.*ENABLE_INVESTMENT_FEATURES.*saka|if.*saka.*ENABLE_INVESTMENT_FEATURES',
            r'if.*finance.*saka|if.*saka.*finance',
            r'if.*investment.*saka|if.*saka.*investment',
            r'saka.*=.*None.*if.*investment|saka.*=.*None.*if.*finance',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : La structure instrumentale (EUR) contraint SAKA dans {saka_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : SAKA est PRIORITAIRE et ne doit JAMAIS être contraint par EUR."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_INVESTMENT_FEATURES=False,
        ENABLE_SAKA=True,  # SAKA doit être activé pour fonctionner
    )
    def test_aucun_impact_saka_si_finance_desactivee(self):
        """
        Vérifie qu'il n'y a aucun impact sur SAKA si les features finance sont désactivées.
        
        RÈGLE ABSOLUE : SAKA fonctionne indépendamment de l'état des features finance.
        """
        from django.contrib.auth import get_user_model
        from core.services.saka import harvest_saka, get_saka_balance, SakaReason
        from core.models.saka import SakaWallet
        
        User = get_user_model()
        
        user = User.objects.create_user(
            username='test_saka_independent_finance',
            email='test_saka_independent_finance@example.com',
            password='testpass123'
        )
        
        # Vérifier que get_saka_balance fonctionne
        balance = get_saka_balance(user)
        assert balance is not None, (
            "VIOLATION CONSTITUTION EGOEJO : get_saka_balance a retourné None.\n"
            "SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
        
        assert 'balance' in balance, (
            "VIOLATION CONSTITUTION EGOEJO : get_saka_balance ne retourne pas la structure attendue.\n"
            "SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
        
        # Vérifier que harvest_saka fonctionne
        harvest_result = harvest_saka(user, SakaReason.CONTENT_READ, amount=50)
        assert harvest_result is not None, (
            "VIOLATION CONSTITUTION EGOEJO : harvest_saka a échoué.\n"
            "SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
        
        # Vérifier que le wallet SAKA existe et fonctionne
        wallet = user.saka_wallet
        assert wallet is not None, (
            "VIOLATION CONSTITUTION EGOEJO : Le wallet SAKA n'existe pas.\n"
            "SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == 50, (
            f"VIOLATION CONSTITUTION EGOEJO : Le solde SAKA n'a pas été mis à jour.\n"
            f"Solde attendu : 50, Solde actuel : {wallet.balance}\n\n"
            f"ACTION REQUISE : SAKA DOIT fonctionner indépendamment de ENABLE_INVESTMENT_FEATURES."
        )

