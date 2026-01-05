"""
Tests de conformité : La banque dormante (EUR) ne touche pas SAKA

PHILOSOPHIE EGOEJO :
- La structure instrumentale (EUR) est DORMANTE
- Elle ne doit pas perturber la structure relationnelle (SAKA)
- Aucune dépendance EUR → SAKA n'est autorisée

Ces tests vérifient que les modules EUR n'importent pas ou n'utilisent pas SAKA.
"""
import re
from pathlib import Path
import pytest


@pytest.mark.egoejo_compliance
class TestBanqueDormanteNeTouchePasSaka:
    """
    Tests de conformité : Vérification que la banque dormante (EUR) ne touche pas SAKA
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.fixture
    def finance_service_path(self):
        """Chemin vers le service Finance"""
        return Path(__file__).parent.parent.parent / "finance" / "services.py"
    
    @pytest.fixture
    def finance_model_path(self):
        """Chemin vers le modèle Finance"""
        return Path(__file__).parent.parent.parent / "finance" / "models.py"
    
    @pytest.fixture
    def investment_model_path(self):
        """Chemin vers le modèle Investment"""
        investment_path = Path(__file__).parent.parent.parent / "investment" / "models.py"
        if investment_path.exists():
            return investment_path
        return None
    
    def test_finance_ne_importe_pas_saka(self, finance_service_path):
        """
        Vérifie que les services Finance n'importent pas SAKA.
        
        RÈGLE ABSOLUE : La structure instrumentale (EUR) ne doit pas dépendre de SAKA.
        """
        if not finance_service_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'finance/services.py' est introuvable. "
                f"Chemin attendu : {finance_service_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la dépendance Finance/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(finance_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : imports SAKA
        forbidden_patterns = [
            r'from.*saka.*import',
            r'import.*saka',
            r'from.*core\.models\.saka',
            r'from.*core\.services\.saka',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Import SAKA dans services Finance.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : La structure instrumentale (EUR) ne doit pas dépendre de SAKA."
        )
    
    def test_finance_ne_reference_pas_saka(self, finance_service_path):
        """
        Vérifie que les services Finance ne référencent pas SAKA dans le code.
        
        RÈGLE ABSOLUE : La structure instrumentale (EUR) ne doit pas utiliser SAKA.
        """
        if not finance_service_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'finance/services.py' est introuvable. "
                f"Chemin attendu : {finance_service_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la dépendance Finance/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(finance_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : références SAKA
        forbidden_patterns = [
            r'SakaWallet',
            r'SakaTransaction',
            r'SakaSilo',
            r'harvest_saka|spend_saka',
            r'saka_wallet|saka_transaction',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Référence SAKA dans services Finance.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : La structure instrumentale (EUR) ne doit pas utiliser SAKA."
        )
    
    def test_finance_modeles_ne_reference_pas_saka(self, finance_model_path):
        """
        Vérifie que les modèles Finance ne référencent pas SAKA.
        
        RÈGLE ABSOLUE : Les modèles EUR ne doivent pas avoir de ForeignKey vers SAKA.
        """
        if not finance_model_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'finance/models.py' est introuvable. "
                f"Chemin attendu : {finance_model_path}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la dépendance Finance/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(finance_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : références SAKA dans modèles
        forbidden_patterns = [
            r'ForeignKey.*SakaWallet',
            r'ForeignKey.*SakaTransaction',
            r'OneToOneField.*SakaWallet',
            r'ManyToManyField.*Saka',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Référence SAKA dans modèles Finance.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Les modèles EUR ne doivent pas référencer SAKA."
        )
    
    def test_investment_ne_touche_pas_saka(self, investment_model_path):
        """
        Vérifie que les modèles Investment n'importent pas ou ne référencent pas SAKA.
        
        RÈGLE ABSOLUE : La structure instrumentale (Investment/EUR) ne doit pas toucher SAKA.
        """
        if investment_model_path is None or not investment_model_path.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le module Investment est introuvable ou non activé. "
                f"Chemin attendu : {investment_model_path}. "
                f"Ce module est OBLIGATOIRE pour la conformité EGOEJO (même s'il est dormant). "
                f"Sans ce module, les protections contre la dépendance Investment/SAKA ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        with open(investment_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : imports et références SAKA
        forbidden_patterns = [
            r'from.*saka.*import',
            r'import.*saka',
            r'SakaWallet|SakaTransaction|SakaSilo',
            r'harvest_saka|spend_saka',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Référence SAKA dans modèles Investment.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : La structure instrumentale (Investment/EUR) ne doit pas toucher SAKA."
        )

