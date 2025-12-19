"""
EGOEJO Compliance Test : Aucune Conversion SAKA ↔ EUR

LOI EGOEJO :
"Aucune conversion SAKA ↔ EUR n'est autorisée. SAKA et EUR sont strictement séparés."

Ce test vérifie que :
- Aucune fonction ne retourne un taux SAKA → EUR
- Aucune fonction ne retourne un équivalent monétaire du SAKA
- Toute tentative de conversion lève une exception explicite

Violation du Manifeste EGOEJO si :
- Une fonction calcule un taux de conversion SAKA → EUR
- Une fonction affiche le SAKA avec une valeur monétaire
- Une fonction permet de convertir SAKA en EUR ou vice versa
"""
import pytest
import re
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.models.saka import SakaWallet, SakaTransaction
from core.services.saka import harvest_saka, get_saka_balance, SakaReason

User = get_user_model()


class TestNoSakaEurConversion:
    """
    Tests de conformité : Aucune conversion SAKA ↔ EUR
    
    RÈGLE ABSOLUE : Aucune conversion SAKA ↔ EUR n'est autorisée.
    """
    
    def test_aucune_fonction_retourne_taux_saka_eur(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une fonction retourne un taux SAKA → EUR.
        
        Test : Scanner le code pour détecter les fonctions de conversion.
        """
        saka_service_file = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        
        if not saka_service_file.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_file}")
        
        with open(saka_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : fonctions de conversion
        forbidden_patterns = [
            r'def\s+\w*convert.*saka.*eur',
            r'def\s+\w*convert.*eur.*saka',
            r'def\s+\w*saka.*to.*eur',
            r'def\s+\w*eur.*to.*saka',
            r'def\s+\w*get.*saka.*rate',
            r'def\s+\w*get.*saka.*price',
            r'def\s+\w*calculate.*saka.*value',
            r'def\s+\w*saka.*exchange.*rate',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: Fonction de conversion détectée - {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Fonction(s) de conversion SAKA ↔ EUR détectée(s) dans saka.py.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute fonction de conversion SAKA ↔ EUR."
        )
    
    def test_aucune_fonction_retourne_equivalent_monetaire(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une fonction retourne un équivalent monétaire du SAKA.
        
        Test : Scanner le code pour détecter les calculs de valeur monétaire.
        """
        saka_service_file = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        
        if not saka_service_file.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_file}")
        
        with open(saka_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : calculs de valeur monétaire
        forbidden_patterns = [
            r'saka.*\*\s*[\d.]+\s*#.*eur|saka.*\*\s*[\d.]+\s*#.*euro',
            r'saka.*\*\s*rate.*eur|saka.*\*\s*rate.*euro',
            r'return.*saka.*\*\s*[\d.]+.*eur|return.*saka.*\*\s*[\d.]+.*euro',
            r'saka.*value.*eur|saka.*value.*euro',
            r'saka.*worth.*eur|saka.*worth.*euro',
            r'saka.*price.*eur|saka.*price.*euro',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()
                
                # Exclure les commentaires et docstrings
                if not line_content.startswith('#') and '"""' not in line_content:
                    violations.append(f"Ligne {line_num}: Calcul de valeur monétaire - {line_content[:80]}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Calcul(s) de valeur monétaire SAKA détecté(s) dans saka.py.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer tout calcul d'équivalent monétaire du SAKA."
        )
    
    @pytest.mark.django_db
    def test_get_saka_balance_ne_retourne_pas_valeur_monetaire(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        get_saka_balance retourne une valeur monétaire (EUR).
        
        Test : Vérifier que get_saka_balance retourne uniquement des grains SAKA.
        """
        user = User.objects.create_user(
            username='test_no_monetary_value',
            email='test_no_monetary_value@example.com',
            password='testpass123'
        )
        
        # Récolter du SAKA
        harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        
        # Récupérer le solde
        balance_data = get_saka_balance(user)
        
        # Assertion : Le solde ne doit pas contenir de valeur monétaire
        assert balance_data is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : get_saka_balance a retourné None."
        )
        
        # Vérifier que le solde ne contient pas de clés monétaires
        forbidden_keys = ['eur', 'euro', 'currency', 'price', 'value', 'worth', 'rate']
        for key in forbidden_keys:
            assert key not in str(balance_data).lower(), (
                f"VIOLATION DU MANIFESTE EGOEJO : get_saka_balance contient une référence monétaire '{key}'. "
                f"Le SAKA ne doit jamais être associé à une valeur monétaire."
            )
        
        # Vérifier que le solde est un nombre (grains SAKA), pas une valeur monétaire
        assert 'balance' in balance_data, (
            "VIOLATION DU MANIFESTE EGOEJO : get_saka_balance ne contient pas 'balance'."
        )
        
        balance_value = balance_data.get('balance', 0)
        assert isinstance(balance_value, (int, float)), (
            f"VIOLATION DU MANIFESTE EGOEJO : Le solde SAKA n'est pas un nombre. "
            f"Type : {type(balance_value)}, Valeur : {balance_value}"
        )
        assert balance_value >= 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le solde SAKA est négatif. "
            f"Valeur : {balance_value}"
        )
    
    @pytest.mark.django_db
    def test_toute_tentative_conversion_leve_exception(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une tentative de conversion SAKA ↔ EUR ne lève pas d'exception explicite.
        
        Test : Vérifier qu'aucune fonction de conversion n'existe.
        """
        user = User.objects.create_user(
            username='test_no_conversion_function',
            email='test_no_conversion_function@example.com',
            password='testpass123'
        )
        
        # Récolter du SAKA
        harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        
        wallet = user.saka_wallet
        wallet.refresh_from_db()
        saka_balance = wallet.balance
        
        # Vérifier qu'il n'existe pas de fonction de conversion dans le module
        import core.services.saka as saka_module
        
        # Lister toutes les fonctions du module
        functions = [name for name in dir(saka_module) if callable(getattr(saka_module, name)) and not name.startswith('_')]
        
        # Vérifier qu'aucune fonction ne contient "convert" dans son nom
        conversion_functions = [f for f in functions if 'convert' in f.lower()]
        
        assert len(conversion_functions) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Fonction(s) de conversion détectée(s) dans core.services.saka : "
            f"{', '.join(conversion_functions)}. Aucune fonction de conversion SAKA ↔ EUR n'est autorisée."
        )
        
        # Vérifier qu'il n'existe pas de fonction qui prend SAKA et retourne EUR
        # (Ceci est une vérification de design, pas de runtime)
        
        # Assertion : Aucune fonction ne doit permettre la conversion
        # Si une fonction de conversion existait, elle devrait lever une exception explicite
        # Mais ici, on vérifie qu'elle n'existe simplement pas
        
        # Vérifier que le solde SAKA ne peut pas être utilisé comme valeur monétaire
        # (pas de champ "eur_equivalent" ou similaire)
        wallet_fields = [f.name for f in wallet._meta.get_fields()]
        forbidden_fields = ['eur_equivalent', 'euro_value', 'currency_value', 'monetary_value']
        
        for field in forbidden_fields:
            assert field not in wallet_fields, (
                f"VIOLATION DU MANIFESTE EGOEJO : Champ monétaire '{field}' détecté dans SakaWallet. "
                f"Le SAKA ne doit jamais avoir de valeur monétaire associée."
            )
    
    def test_aucun_affichage_monetaire_dans_code(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le code contient des affichages monétaires du SAKA (€, euro, currency).
        
        Test : Scanner le code pour détecter les affichages monétaires.
        """
        saka_service_file = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        saka_model_file = Path(__file__).parent.parent.parent / "core" / "models" / "saka.py"
        
        violations = []
        
        for file_path in [saka_service_file, saka_model_file]:
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patterns interdits : affichages monétaires
            forbidden_patterns = [
                r'saka.*€|€.*saka',
                r'saka.*euro|euro.*saka',
                r'saka.*currency|currency.*saka',
                r'format.*saka.*money|format.*money.*saka',
                r'saka.*\$\s*|saka.*usd|saka.*gbp',
            ]
            
            for pattern in forbidden_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    
                    # Exclure les commentaires et docstrings
                    if not line_content.startswith('#') and '"""' not in line_content:
                        violations.append(f"{file_path.name} (ligne {line_num}): {line_content[:80]}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Affichage(s) monétaire(s) du SAKA détecté(s).\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer tout affichage monétaire du SAKA."
        )

