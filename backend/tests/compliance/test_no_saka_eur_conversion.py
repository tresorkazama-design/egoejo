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


@pytest.mark.egoejo_compliance
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
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'core/services/saka.py' est introuvable. "
                f"Chemin attendu : {saka_service_file}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la conversion SAKA/EUR ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
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
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'core/services/saka.py' est introuvable. "
                f"Chemin attendu : {saka_service_file}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la conversion SAKA/EUR ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
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
            pytest.fail(
                "PROTECTION MANQUANTE : SAKA est désactivé dans cet environnement de test. "
                "SAKA doit être ACTIVÉ pour tous les tests de compliance EGOEJO. "
                "Sans SAKA activé, les protections philosophiques ne peuvent pas être vérifiées. "
                "Conformité EGOEJO VIOLÉE. "
                "Action requise : Configurer ENABLE_SAKA=True dans les variables d'environnement de test."
            )
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
    
    def test_scan_recursif_tous_fichiers_python_backend(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un fichier Python du backend contient des patterns interdits.
        
        Test : Scanner récursivement TOUS les fichiers Python du backend pour détecter :
        - Conversion monétaire SAKA ↔ EUR ou autre devise
        - Accumulation financière
        - Équivalence SAKA ↔ monnaie fiat
        
        Le test FAIL si un seul pattern est trouvé.
        """
        backend_dir = Path(__file__).parent.parent.parent
        
        # Patterns interdits explicites (liste complète)
        FORBIDDEN_PATTERNS = [
            # Conversion SAKA ↔ EUR
            (r'convert.*saka.*eur', 'Conversion SAKA vers EUR'),
            (r'convert.*eur.*saka', 'Conversion EUR vers SAKA'),
            (r'saka.*to.*eur', 'Conversion SAKA vers EUR (to)'),
            (r'eur.*to.*saka', 'Conversion EUR vers SAKA (to)'),
            (r'saka.*exchange.*rate.*eur', 'Taux de change SAKA/EUR'),
            (r'eur.*exchange.*rate.*saka', 'Taux de change EUR/SAKA'),
            (r'saka.*\*\s*eur.*rate', 'Calcul SAKA * taux EUR'),
            (r'eur.*rate.*\*\s*saka', 'Calcul taux EUR * SAKA'),
            (r'saka.*\*\s*exchange_rate', 'Calcul SAKA * taux de change'),
            (r'exchange_rate.*\*\s*saka', 'Calcul taux de change * SAKA'),
            
            # Conversion SAKA ↔ autres devises
            (r'convert.*saka.*(?:usd|gbp|chf|jpy|cad|aud)', 'Conversion SAKA vers autre devise'),
            (r'convert.*(?:usd|gbp|chf|jpy|cad|aud).*saka', 'Conversion autre devise vers SAKA'),
            (r'saka.*to.*(?:usd|gbp|chf|jpy|cad|aud)', 'Conversion SAKA vers autre devise (to)'),
            (r'(?:usd|gbp|chf|jpy|cad|aud).*to.*saka', 'Conversion autre devise vers SAKA (to)'),
            
            # Valeur monétaire du SAKA
            (r'saka.*\*\s*[\d.]+.*eur', 'Calcul valeur SAKA en EUR'),
            (r'saka.*\*\s*[\d.]+.*usd', 'Calcul valeur SAKA en USD'),
            (r'saka.*value.*eur', 'Valeur SAKA en EUR'),
            (r'saka.*value.*usd', 'Valeur SAKA en USD'),
            (r'saka.*worth.*eur', 'Valeur SAKA en EUR (worth)'),
            (r'saka.*worth.*usd', 'Valeur SAKA en USD (worth)'),
            (r'saka.*price.*eur', 'Prix SAKA en EUR'),
            (r'saka.*price.*usd', 'Prix SAKA en USD'),
            (r'eur.*equivalent.*saka', 'Équivalent EUR du SAKA'),
            (r'usd.*equivalent.*saka', 'Équivalent USD du SAKA'),
            (r'saka.*equivalent.*eur', 'Équivalent SAKA en EUR'),
            (r'saka.*equivalent.*usd', 'Équivalent SAKA en USD'),
            (r'return.*saka.*\*\s*[\d.]+.*eur', 'Retour valeur SAKA en EUR'),
            (r'return.*saka.*\*\s*[\d.]+.*usd', 'Retour valeur SAKA en USD'),
            
            # Accumulation financière
            (r'saka.*accumulate', 'Accumulation SAKA'),
            (r'saka.*interest', 'Intérêt sur SAKA'),
            (r'saka.*yield', 'Rendement SAKA'),
            (r'saka.*return.*rate', 'Taux de rendement SAKA'),
            (r'saka.*profit', 'Profit SAKA'),
            (r'saka.*dividend', 'Dividende SAKA'),
            (r'saka.*investment', 'Investissement SAKA'),
            (r'saka.*speculation', 'Spéculation SAKA'),
            
            # Affichage monétaire
            (r'saka.*€', 'Affichage SAKA avec symbole €'),
            (r'saka.*\$', 'Affichage SAKA avec symbole $'),
            (r'saka.*eur', 'Affichage SAKA avec EUR'),
            (r'saka.*usd', 'Affichage SAKA avec USD'),
            (r'saka.*gbp', 'Affichage SAKA avec GBP'),
            (r'format.*saka.*currency', 'Format SAKA comme devise'),
            (r'format.*currency.*saka', 'Format devise pour SAKA'),
            (r'saka.*currency', 'SAKA comme devise'),
            (r'currency.*saka', 'Devise SAKA'),
        ]
        
        # Compiler tous les patterns
        compiled_patterns = []
        for pattern_str, description in FORBIDDEN_PATTERNS:
            try:
                compiled_patterns.append((re.compile(pattern_str, re.IGNORECASE), description))
            except re.error as e:
                pytest.fail(f"Pattern regex invalide : {pattern_str} - {e}")
        
        # Collecter tous les fichiers Python du backend
        python_files = []
        excluded_dirs = {
            '__pycache__', 'migrations', 'venv', 'env', '.venv', 
            'htmlcov', 'staticfiles', 'media', 'test-results',
            'node_modules', '.git'
        }
        
        for py_file in backend_dir.rglob('*.py'):
            # Exclure les fichiers dans les dossiers interdits
            parts = py_file.parts
            if any(excluded in parts for excluded in excluded_dirs):
                continue
            
            # Exclure les fichiers de test (sauf les tests de compliance)
            if 'tests' in parts and 'compliance' not in parts:
                continue
            
            # Exclure les fichiers de test dans le dossier racine
            if py_file.name.startswith('test_') and 'compliance' not in py_file.parts:
                continue
            
            python_files.append(py_file)
        
        # Scanner tous les fichiers
        all_violations = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
            except (UnicodeDecodeError, PermissionError) as e:
                # Ignorer les fichiers non lisibles
                continue
            
            # Scanner avec chaque pattern
            for compiled_pattern, description in compiled_patterns:
                for match in compiled_pattern.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''
                    
                    # Exclure les commentaires et docstrings
                    stripped_line = line_content.lstrip()
                    if stripped_line.startswith('#') or stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                        continue
                    
                    # Exclure les docstrings multilignes (début ou fin)
                    # Vérifier si on est dans une docstring
                    before_match = content[:match.start()]
                    # Compter les """ et ''' avant la position du match
                    triple_double = before_match.count('"""')
                    triple_single = before_match.count("'''")
                    # Si nombre impair, on est dans une docstring
                    if triple_double % 2 == 1 or triple_single % 2 == 1:
                        continue
                    
                    # Extraire le contexte (ligne précédente et suivante si disponible)
                    context_lines = []
                    if line_num > 1:
                        context_lines.append(f"  {line_num - 1:4d} | {lines[line_num - 2].rstrip()}")
                    context_lines.append(f"  {line_num:4d} | {line_content}")
                    if line_num < len(lines):
                        context_lines.append(f"  {line_num + 1:4d} | {lines[line_num].rstrip()}")
                    
                    violation = {
                        'file': str(py_file.relative_to(backend_dir)),
                        'line': line_num,
                        'pattern': description,
                        'match': match.group()[:100],  # Limiter la longueur
                        'code': line_content[:120],  # Limiter la longueur
                        'context': '\n'.join(context_lines)
                    }
                    all_violations.append(violation)
        
        # Générer le rapport détaillé
        if all_violations:
            report_lines = [
                "=" * 80,
                "VIOLATION DU MANIFESTE EGOEJO : Patterns interdits détectés",
                "=" * 80,
                "",
                f"Nombre total de violations : {len(all_violations)}",
                "",
            ]
            
            # Grouper par fichier
            violations_by_file = {}
            for v in all_violations:
                file_key = v['file']
                if file_key not in violations_by_file:
                    violations_by_file[file_key] = []
                violations_by_file[file_key].append(v)
            
            for file_path, violations in sorted(violations_by_file.items()):
                report_lines.extend([
                    f"\n📁 Fichier : {file_path}",
                    f"   Violations : {len(violations)}",
                    "-" * 80,
                ])
                
                for v in violations:
                    report_lines.extend([
                        f"  ❌ Ligne {v['line']} : {v['pattern']}",
                        f"     Match : {v['match']}",
                        f"     Code : {v['code']}",
                        f"     Contexte :",
                        v['context'],
                        "",
                    ])
            
            report_lines.extend([
                "=" * 80,
                "ACTION REQUISE : Supprimer toutes les violations détectées.",
                "=" * 80,
            ])
            
            report = "\n".join(report_lines)
            
            pytest.fail(
                f"\n{report}\n\n"
                f"Le test FAIL car {len(all_violations)} violation(s) a/ont été détectée(s). "
                f"Toute violation doit être corrigée avant de pouvoir continuer."
            )
        
        # Si aucune violation, le test passe
        assert len(all_violations) == 0, "Aucune violation ne devrait être détectée si le test arrive ici."