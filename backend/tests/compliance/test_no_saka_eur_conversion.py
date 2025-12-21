"""
EGOEJO Compliance Test : Aucune Conversion SAKA vers monnaie fiat

LOI EGOEJO :
"Aucune conversion SAKA vers monnaie fiat n'est autorisée. SAKA et monnaie fiat sont strictement séparés."

Ce test vérifie que :
- Aucune fonction ne retourne un taux SAKA vers monnaie fiat
- Aucune fonction ne retourne un équivalent monétaire du SAKA
- Toute tentative de conversion lève une exception explicite

Violation du Manifeste EGOEJO si :
- Une fonction calcule un taux de conversion SAKA vers monnaie fiat
- Une fonction affiche le SAKA avec une valeur fiduciaire
- Une fonction permet de convertir SAKA en monnaie fiat ou vice versa
"""
import pytest
import re
import json
import base64
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.models.saka import SakaWallet, SakaTransaction
from core.services.saka import harvest_saka, get_saka_balance, SakaReason

User = get_user_model()


# ============================================================================
# SINGLETON PATTERN : Chargement et compilation UNE SEULE FOIS au démarrage
# ============================================================================

# Cache module-level pour les patterns compilés (chargés une seule fois)
_COMPILED_PATTERNS = None
_PATTERNS_FILE_PATH = Path(__file__).parent / "test_patterns.json"


def _load_and_compile_patterns():
    """
    Charge le fichier JSON, décode les patterns Base64 et compile les regex.
    
    Cette fonction est appelée UNE SEULE FOIS au chargement du module.
    Fail-fast : lève une exception si le fichier est manquant ou invalide.
    
    Returns:
        dict: Dictionnaire avec les patterns compilés :
            - 'conversion': Liste de regex compilées pour les fonctions de conversion
            - 'monetary_value': Liste de regex compilées pour les calculs de valeur
            - 'display': Liste de regex compilées pour les affichages
    
    Raises:
        FileNotFoundError: Si test_patterns.json n'existe pas
        ValueError: Si le JSON est invalide ou les patterns corrompus
        re.error: Si un pattern regex est invalide
    """
    global _COMPILED_PATTERNS
    
    if _COMPILED_PATTERNS is not None:
        return _COMPILED_PATTERNS
    
    # FAIL-FAST : Lever exception si fichier manquant
    if not _PATTERNS_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Fichier de patterns requis introuvable : {_PATTERNS_FILE_PATH}\n"
            f"Ce fichier est OBLIGATOIRE pour les tests de conformité. "
            f"Les tests DOIVENT échouer si les règles sont absentes."
        )
    
    # Charger le JSON (UNE SEULE FOIS)
    try:
        with open(_PATTERNS_FILE_PATH, 'r', encoding='utf-8') as f:
            patterns_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Fichier JSON invalide : {_PATTERNS_FILE_PATH}\n"
            f"Erreur de parsing : {e}"
        ) from e
    
    # Décoder et compiler les patterns (UNE SEULE FOIS)
    compiled = {}
    
    # Patterns de conversion
    conv_encoded = patterns_data.get('conv_enc', [])
    if not conv_encoded:
        raise ValueError(f"Clé 'conv_enc' manquante ou vide dans {_PATTERNS_FILE_PATH}")
    
    compiled['conversion'] = []
    for enc_pattern in conv_encoded:
        try:
            decoded = base64.b64decode(enc_pattern).decode('utf-8')
            # VALIDATION : Compiler le regex pour détecter les erreurs immédiatement
            compiled_pattern = re.compile(decoded, re.IGNORECASE)
            compiled['conversion'].append(compiled_pattern)
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            raise ValueError(
                f"Pattern Base64 invalide dans 'conv_enc' : {enc_pattern[:50]}...\n"
                f"Erreur : {e}"
            ) from e
        except re.error as e:
            raise ValueError(
                f"Pattern regex invalide après décodage : {decoded[:50]}...\n"
                f"Erreur regex : {e}"
            ) from e
    
    # Patterns de valeur monétaire
    fiat_val_encoded = patterns_data.get('fiat_val_enc', [])
    if not fiat_val_encoded:
        raise ValueError(f"Clé 'fiat_val_enc' manquante ou vide dans {_PATTERNS_FILE_PATH}")
    
    compiled['monetary_value'] = []
    for enc_pattern in fiat_val_encoded:
        try:
            decoded = base64.b64decode(enc_pattern).decode('utf-8')
            compiled_pattern = re.compile(decoded, re.IGNORECASE)
            compiled['monetary_value'].append(compiled_pattern)
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            raise ValueError(
                f"Pattern Base64 invalide dans 'fiat_val_enc' : {enc_pattern[:50]}...\n"
                f"Erreur : {e}"
            ) from e
        except re.error as e:
            raise ValueError(
                f"Pattern regex invalide après décodage : {decoded[:50]}...\n"
                f"Erreur regex : {e}"
            ) from e
    
    # Patterns d'affichage
    fiat_disp_encoded = patterns_data.get('fiat_disp_enc', [])
    if not fiat_disp_encoded:
        raise ValueError(f"Clé 'fiat_disp_enc' manquante ou vide dans {_PATTERNS_FILE_PATH}")
    
    compiled['display'] = []
    for enc_pattern in fiat_disp_encoded:
        try:
            decoded = base64.b64decode(enc_pattern).decode('utf-8')
            compiled_pattern = re.compile(decoded, re.IGNORECASE)
            compiled['display'].append(compiled_pattern)
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            raise ValueError(
                f"Pattern Base64 invalide dans 'fiat_disp_enc' : {enc_pattern[:50]}...\n"
                f"Erreur : {e}"
            ) from e
        except re.error as e:
            raise ValueError(
                f"Pattern regex invalide après décodage : {decoded[:50]}...\n"
                f"Erreur regex : {e}"
            ) from e
    
    _COMPILED_PATTERNS = compiled
    return compiled


# Constantes pour les clés interdites (lisibles, pas de chr() illisible)
FORBIDDEN_MONETARY_KEYS = ['eur', 'euro', 'currency', 'price', 'value', 'worth', 'rate']
FORBIDDEN_MONETARY_FIELDS = ['eur_equivalent', 'euro_value', 'currency_value', 'monetary_value']


# Initialisation au chargement du module (FAIL-FAST)
try:
    _PATTERNS = _load_and_compile_patterns()
except (FileNotFoundError, ValueError, re.error) as e:
    # En cas d'erreur, on stocke l'exception pour la lever dans chaque test
    _PATTERNS_ERROR = e
    _PATTERNS = None
else:
    _PATTERNS_ERROR = None


class TestNoSakaEurConversion:
    """
    Tests de conformité : Aucune conversion SAKA vers monnaie fiat
    
    RÈGLE ABSOLUE : Aucune conversion SAKA vers monnaie fiat n'est autorisée.
    """
    
    def setup_method(self):
        """Vérifie que les patterns sont chargés avant chaque test (fail-fast)"""
        if _PATTERNS_ERROR is not None:
            pytest.fail(
                f"ERREUR CRITIQUE : Impossible de charger les patterns de test.\n"
                f"{_PATTERNS_ERROR}\n\n"
                f"Les tests de conformité REQUIÈRENT le fichier test_patterns.json. "
                f"Ils DOIVENT échouer si les règles sont absentes."
            )
    
    def test_aucune_fonction_retourne_taux_saka_eur(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une fonction retourne un taux SAKA vers monnaie fiat.
        
        Test : Scanner le code pour détecter les fonctions de conversion.
        """
        saka_service_file = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        
        if not saka_service_file.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_file}")
        
        # Lire le fichier UNE SEULE FOIS
        with open(saka_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Utiliser les patterns compilés (déjà chargés et compilés)
        violations = []
        for compiled_pattern in _PATTERNS['conversion']:
            matches = compiled_pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"Ligne {line_num}: Fonction de conversion détectée - {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Fonction(s) de conversion SAKA vers monnaie fiat détectée(s) dans saka.py.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute fonction de conversion SAKA vers monnaie fiat."
        )
    
    def test_aucune_fonction_retourne_equivalent_monetaire(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une fonction retourne un équivalent monétaire du SAKA.
        
        Test : Scanner le code pour détecter les calculs de valeur fiduciaire.
        """
        saka_service_file = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        
        if not saka_service_file.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_file}")
        
        # Lire le fichier UNE SEULE FOIS
        with open(saka_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Utiliser les patterns compilés (déjà chargés et compilés)
        violations = []
        for compiled_pattern in _PATTERNS['monetary_value']:
            matches = compiled_pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()
                
                # Exclure les commentaires et docstrings
                if not line_content.startswith('#') and '"""' not in line_content:
                    violations.append(f"Ligne {line_num}: Calcul de valeur fiduciaire - {line_content[:80]}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Calcul(s) de valeur fiduciaire SAKA détecté(s) dans saka.py.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer tout calcul d'équivalent monétaire du SAKA."
        )
    
    @pytest.mark.django_db
    def test_get_saka_balance_ne_retourne_pas_valeur_monetaire(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        get_saka_balance retourne une valeur fiduciaire.
        
        Test : Vérifier que get_saka_balance retourne uniquement des grains SAKA.
        """
        user = User.objects.create_user(
            username='test_no_fiat_value',
            email='test_no_fiat_value@example.com',
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
        
        # Vérifier que le solde ne contient pas de clés monétaires (constantes lisibles)
        for key in FORBIDDEN_MONETARY_KEYS:
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
        Une tentative de conversion SAKA vers monnaie fiat ne lève pas d'exception explicite.
        
        Test : Vérifier qu'aucune fonction de conversion n'existe.
        """
        user = User.objects.create_user(
            username='test_no_conversion_function',
            email='test_no_conversion_function@example.com',
            password='testpass123'
        )
        
        # Récolter du SAKA
        harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        
        # S'assurer que le wallet existe (créé par harvest_saka si SAKA est activé)
        from core.services.saka import get_or_create_wallet
        wallet = get_or_create_wallet(user)
        if wallet is None:
            pytest.skip("SAKA is disabled in this test environment")
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
            f"{', '.join(conversion_functions)}. Aucune fonction de conversion SAKA vers monnaie fiat n'est autorisée."
        )
        
        # Vérifier que le solde SAKA ne peut pas être utilisé comme valeur monétaire
        # (pas de champ "eur_equivalent" ou similaire)
        wallet_fields = [f.name for f in wallet._meta.get_fields()]
        
        # Utiliser les constantes lisibles (pas de chr() illisible)
        for field in FORBIDDEN_MONETARY_FIELDS:
            assert field not in wallet_fields, (
                f"VIOLATION DU MANIFESTE EGOEJO : Champ monétaire '{field}' détecté dans SakaWallet. "
                f"Le SAKA ne doit jamais avoir de valeur monétaire associée."
            )
    
    def test_aucun_affichage_monetaire_dans_code(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le code contient des affichages interdits du SAKA (symboles, devise).
        
        Test : Scanner le code pour détecter les affichages interdits.
        """
        saka_service_file = Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
        saka_model_file = Path(__file__).parent.parent.parent / "core" / "models" / "saka.py"
        
        violations = []
        
        for file_path in [saka_service_file, saka_model_file]:
            if not file_path.exists():
                continue
            
            # Lire le fichier UNE SEULE FOIS
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Utiliser les patterns compilés (déjà chargés et compilés)
            for compiled_pattern in _PATTERNS['display']:
                matches = compiled_pattern.finditer(content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    
                    # Exclure les commentaires et docstrings
                    if not line_content.startswith('#') and '"""' not in line_content:
                        violations.append(f"{file_path.name} (ligne {line_num}): {line_content[:80]}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Affichage(s) interdit(s) du SAKA détecté(s).\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer tout affichage interdit du SAKA."
        )
