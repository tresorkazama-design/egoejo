"""
Tests de conformité : Aucun rendement financier basé sur SAKA

PHILOSOPHIE EGOEJO :
- Aucun rendement financier basé sur SAKA n'est autorisé
- Le SAKA est une monnaie d'engagement, pas d'investissement
- Pas d'intérêt, dividende, yield, profit ou return sur SAKA

Ces tests analysent le code réel pour détecter toute violation.
"""
import re
from pathlib import Path
import pytest


class TestSakaNoFinancialReturn:
    """
    Tests de conformité : Vérification de l'absence de rendement financier basé sur SAKA
    """
    
    @pytest.fixture
    def saka_service_path(self):
        """Chemin vers le service SAKA"""
        return Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
    
    @pytest.fixture
    def saka_model_path(self):
        """Chemin vers le modèle SAKA"""
        return Path(__file__).parent.parent.parent / "core" / "models" / "saka.py"
    
    def test_aucun_rendement_financier_saka(self, saka_service_path):
        """
        Vérifie qu'il n'existe aucune logique de rendement financier basé sur SAKA.
        
        RÈGLE ABSOLUE : Aucun rendement financier basé sur SAKA n'est autorisé.
        Le SAKA est une monnaie d'engagement, pas d'investissement.
        """
        if not saka_service_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_path}")
        
        with open(saka_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : rendement financier
        # Plus précis : chercher des patterns de calcul de rendement
        forbidden_patterns = [
            r'saka.*interest.*rate|interest.*rate.*saka',  # Intérêt sur SAKA
            r'saka.*dividend.*payment|dividend.*payment.*saka',  # Dividende basé sur SAKA
            r'saka.*yield.*calculation|yield.*calculation.*saka',  # Rendement SAKA
            r'saka.*profit.*margin|profit.*margin.*saka',  # Profit basé sur SAKA
            r'saka.*return.*on.*investment|return.*on.*investment.*saka',  # ROI SAKA
            r'saka.*roi|roi.*saka',  # Return on Investment SAKA
            r'saka.*apy|apy.*saka',  # Annual Percentage Yield SAKA
            r'calculate.*saka.*interest|calculate.*interest.*saka',  # Calcul d'intérêt
            r'calculate.*saka.*dividend|calculate.*dividend.*saka',  # Calcul de dividende
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Rendement financier basé sur SAKA détecté dans {saka_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute logique de rendement financier basé sur SAKA."
        )
    
    def test_aucun_champ_rendement_dans_modeles_saka(self, saka_model_path):
        """
        Vérifie qu'il n'y a aucun champ de rendement financier dans les modèles SAKA.
        
        RÈGLE ABSOLUE : Les modèles SAKA ne doivent pas contenir de champs liés au rendement financier.
        """
        if not saka_model_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_model_path}")
        
        with open(saka_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : champs de rendement
        forbidden_patterns = [
            r'interest.*=.*models\.',
            r'dividend.*=.*models\.',
            r'yield.*=.*models\.',
            r'profit.*=.*models\.',
            r'roi.*=.*models\.',
            r'apy.*=.*models\.',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Champ de rendement financier dans modèles SAKA.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer tout champ de rendement financier des modèles SAKA."
        )

