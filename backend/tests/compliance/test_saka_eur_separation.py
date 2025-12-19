"""
Tests de conformité : Séparation stricte SAKA ↔ EUR

PHILOSOPHIE EGOEJO :
- Aucune conversion SAKA ↔ EUR n'est autorisée
- SAKA et EUR sont strictement séparés
- Aucun affichage monétaire du SAKA

Ces tests analysent le code réel pour détecter toute violation.
"""
import ast
import inspect
import os
from pathlib import Path
import pytest
import re


class TestSakaEurSeparation:
    """
    Tests de conformité : Vérification de la séparation stricte SAKA ↔ EUR
    """
    
    @pytest.fixture
    def saka_service_path(self):
        """Chemin vers le service SAKA"""
        return Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
    
    @pytest.fixture
    def saka_model_path(self):
        """Chemin vers le modèle SAKA"""
        return Path(__file__).parent.parent.parent / "core" / "models" / "saka.py"
    
    def test_aucune_conversion_saka_eur_dans_code(self, saka_service_path):
        """
        Vérifie qu'il n'existe aucune fonction de conversion SAKA ↔ EUR dans le code.
        
        RÈGLE ABSOLUE : Aucune conversion SAKA ↔ EUR n'est autorisée.
        Le SAKA et l'EUR sont strictement séparés.
        """
        if not saka_service_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_path}")
        
        with open(saka_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : conversion SAKA ↔ EUR
        # Plus précis : chercher des patterns de conversion explicite
        forbidden_patterns = [
            r'convert.*saka.*to.*eur|convert.*eur.*to.*saka',  # Conversion explicite
            r'saka.*=.*eur|eur.*=.*saka',  # Affectation directe
            r'saka.*\*.*eur|eur.*\*.*saka',  # Multiplication (taux de change)
            r'saka.*/.*eur|eur.*/.*saka',  # Division (taux de change)
            r'price.*saka|saka.*price',  # Prix du SAKA
            r'exchange.*saka|saka.*exchange',  # Échange SAKA
            r'rate.*saka.*eur|rate.*eur.*saka',  # Taux de change
            r'value.*saka.*eur|value.*eur.*saka',  # Valeur EUR du SAKA
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Conversion SAKA ↔ EUR détectée dans {saka_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute logique de conversion SAKA ↔ EUR."
        )
    
    def test_aucun_affichage_monetaire_saka(self, saka_service_path):
        """
        Vérifie qu'il n'y a aucun affichage monétaire du SAKA (€, euro, currency).
        
        RÈGLE ABSOLUE : Le SAKA ne doit jamais être affiché comme une monnaie convertible.
        """
        if not saka_service_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_path}")
        
        with open(saka_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : affichage monétaire
        forbidden_patterns = [
            r'saka.*€|€.*saka',
            r'saka.*euro|euro.*saka',
            r'saka.*currency|currency.*saka',
            r'format.*saka.*money|money.*format.*saka',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Affichage monétaire du SAKA détecté dans {saka_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Ne pas afficher le SAKA comme une monnaie convertible."
        )
    
    def test_aucune_reference_eur_dans_services_saka(self, saka_service_path):
        """
        Vérifie qu'il n'y a aucune référence à EUR/investment dans les services SAKA.
        
        RÈGLE ABSOLUE : SAKA et EUR sont strictement séparés.
        Les services SAKA ne doivent pas importer ou utiliser de modules EUR.
        """
        if not saka_service_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_path}")
        
        with open(saka_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les imports
        forbidden_imports = [
            r'from.*finance.*import',
            r'from.*investment.*import',
            r'import.*finance',
            r'import.*investment',
        ]
        
        violations = []
        for pattern in forbidden_imports:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Référence EUR/investment dans services SAKA.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute dépendance SAKA → EUR."
        )
    
    def test_aucune_reference_eur_dans_modeles_saka(self, saka_model_path):
        """
        Vérifie qu'il n'y a aucune référence à EUR/investment dans les modèles SAKA.
        
        RÈGLE ABSOLUE : Les modèles SAKA ne doivent pas référencer les modèles EUR.
        """
        if not saka_model_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_model_path}")
        
        with open(saka_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les imports et références
        forbidden_patterns = [
            r'from.*finance.*import',
            r'from.*investment.*import',
            r'import.*finance',
            r'import.*investment',
            r'ForeignKey.*finance|ForeignKey.*investment',
            r'OneToOneField.*finance|OneToOneField.*investment',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Référence EUR/investment dans modèles SAKA.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute dépendance SAKA → EUR."
        )

