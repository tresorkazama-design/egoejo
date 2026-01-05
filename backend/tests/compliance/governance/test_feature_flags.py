"""
EGOEJO Compliance Test : Feature Flags Respectés

LOI EGOEJO :
"Les feature flags critiques (V2.0, Investment) doivent être respectés. Aucun contournement n'est autorisé."

Ce test vérifie que :
- V2.0 (Investment) ne peut pas être activée sans feature flag
- Les fonctionnalités financières respectent les feature flags
- Aucun contournement de feature flag n'est possible

Violation du Manifeste EGOEJO si :
- Une feature financière contourne un feature flag
- V2.0 est activée sans feature flag
- Les feature flags sont ignorés
"""
import pytest
from django.test import override_settings
from django.conf import settings
from pathlib import Path
import re


@pytest.mark.egoejo_compliance
class TestFeatureFlags:
    """
    Tests de conformité : Feature Flags Respectés
    
    RÈGLE ABSOLUE : Les feature flags critiques doivent être respectés.
    """
    
    def test_v2_investment_ne_peut_pas_etre_activee_sans_flag(self):
        """
        VIOLATION DE LA CONSTITUTION EGOEJO si :
        V2.0 (Investment) peut être activée sans feature flag.
        
        RÈGLE ABSOLUE : V2.0 doit être strictement contrôlé par ENABLE_INVESTMENT_FEATURES.
        Aucun assouplissement temporaire n'est autorisé.
        
        Test : Vérifier que TOUS les points d'entrée V2.0 vérifient le feature flag.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        
        violations = []
        all_checks_passed = True
        
        # 1. Vérifier que le setting ENABLE_INVESTMENT_FEATURES existe et est False par défaut
        settings_file = backend_dir / "config" / "settings.py"
        if not settings_file.exists():
            pytest.fail(
                "VIOLATION CONSTITUTION EGOEJO : "
                "Le fichier settings.py est introuvable. "
                "ENABLE_INVESTMENT_FEATURES doit être défini et False par défaut."
            )
        
        settings_content = settings_file.read_text(encoding="utf-8")
        
        # Vérifier que ENABLE_INVESTMENT_FEATURES est défini
        if "ENABLE_INVESTMENT_FEATURES" not in settings_content:
            violations.append(
                "settings.py : ENABLE_INVESTMENT_FEATURES n'est pas défini. "
                "V2.0 doit être contrôlé par un feature flag."
            )
            all_checks_passed = False
        
        # Vérifier que la valeur par défaut est False
        if "ENABLE_INVESTMENT_FEATURES" in settings_content:
            # Chercher la ligne de définition
            for line in settings_content.split('\n'):
                if 'ENABLE_INVESTMENT_FEATURES' in line and '=' in line:
                    # Vérifier que la valeur par défaut dans os.environ.get() est 'False'
                    # Pattern attendu: os.environ.get('ENABLE_INVESTMENT_FEATURES', 'False')
                    if "os.environ.get" in line:
                        # Extraire la valeur par défaut (deuxième argument de get)
                        import re
                        default_match = re.search(r"\.get\([^,]+,\s*['\"]([^'\"]+)['\"]", line)
                        if default_match:
                            default_value = default_match.group(1).lower()
                            if default_value == 'true':
                                violations.append(
                                    f"settings.py : ENABLE_INVESTMENT_FEATURES a une valeur par défaut True dans os.environ.get(). "
                                    f"La valeur par défaut DOIT être 'False' pour protéger la gouvernance. "
                                    f"Ligne: {line.strip()}"
                                )
                                all_checks_passed = False
                    break
        
        # 2. Vérifier les vues investment (si elles existent)
        investment_views_paths = [
            backend_dir / "finance" / "api" / "investment_views.py",
            backend_dir / "investment" / "views.py",
            backend_dir / "investment" / "api" / "views.py",
        ]
        
        investment_views_found = False
        for investment_views in investment_views_paths:
            if investment_views.exists():
                investment_views_found = True
                content = investment_views.read_text(encoding="utf-8")
                
                # Vérifier que les vues utilisent IsInvestmentFeatureEnabled ou vérifient le flag
                has_protection = (
                    "IsInvestmentFeatureEnabled" in content or
                    "ENABLE_INVESTMENT_FEATURES" in content or
                    "settings.ENABLE_INVESTMENT_FEATURES" in content
                )
                
                if not has_protection:
                    violations.append(
                        f"{investment_views.relative_to(backend_dir.parent)} : "
                        "Les vues investment ne vérifient pas le feature flag ENABLE_INVESTMENT_FEATURES. "
                        "Toutes les vues V2.0 DOIVENT vérifier le flag."
                    )
                    all_checks_passed = False
                
                # Vérifier qu'aucune vue ne force l'activation (hors commentaires)
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    # Ignorer les commentaires
                    if line.strip().startswith('#') or '#' in line and line.split('#')[0].strip() == '':
                        continue
                    # Vérifier si la ligne force l'activation (hors commentaires)
                    if re.search(r'enable.*investment.*=.*true', line, re.IGNORECASE):
                        violations.append(
                            f"{investment_views.relative_to(backend_dir.parent)}:{line_num} : "
                            "Une vue force l'activation d'ENABLE_INVESTMENT_FEATURES. "
                            "C'est une violation de la constitution EGOEJO. "
                            f"Ligne: {line.strip()}"
                        )
                        all_checks_passed = False
        
        # 3. Vérifier les services finance/services.py (point d'entrée principal)
        finance_services = backend_dir / "finance" / "services.py"
        if finance_services.exists():
            content = finance_services.read_text(encoding="utf-8")
            
            # Vérifier que les fonctions EQUITY vérifient le flag
            equity_functions = [
                "pledge_funds",
                "create_equity_pledge",
                "process_equity_investment",
            ]
            
            for func_name in equity_functions:
                if func_name in content:
                    func_def_pattern = re.compile(
                        rf"def\s+{func_name}\s*\(",
                        re.IGNORECASE
                    )
                    func_match = func_def_pattern.search(content)
                    
                    if func_match:
                        # Extraire les 200 lignes suivantes
                        start_pos = func_match.end()
                        lines_after = content[start_pos:start_pos + 5000]
                        
                        # Vérifier la présence de vérification de feature flag
                        # _validate_pledge_request vérifie le flag pour EQUITY, donc c'est acceptable
                        # Mais on doit aussi vérifier directement dans pledge_funds pour EQUITY
                        has_flag_check = (
                            "ENABLE_INVESTMENT_FEATURES" in lines_after or
                            "IsInvestmentFeatureEnabled" in lines_after or
                            "settings.ENABLE_INVESTMENT_FEATURES" in lines_after or
                            ("_validate_pledge_request" in lines_after and func_name != "pledge_funds")  # pledge_funds doit vérifier directement
                        )
                        
                        # Pour pledge_funds, vérifier qu'il y a une vérification directe pour EQUITY
                        if func_name == "pledge_funds":
                            # Vérifier qu'il y a une vérification pour EQUITY
                            has_equity_check = (
                                ("EQUITY" in lines_after and "ENABLE_INVESTMENT" in lines_after) or
                                ("pledge_type" in lines_after and "EQUITY" in lines_after and "ENABLE_INVESTMENT" in lines_after)
                            )
                            if not has_equity_check:
                                has_flag_check = False
                        
                        if not has_flag_check:
                            violations.append(
                                f"finance/services.py : {func_name}() ne vérifie pas ENABLE_INVESTMENT_FEATURES. "
                                "Toutes les fonctions EQUITY DOIVENT vérifier le flag."
                            )
                            all_checks_passed = False
        
        # 4. Vérifier les modèles investment (si ils existent)
        investment_models_paths = [
            backend_dir / "investment" / "models.py",
        ]
        
        for investment_models in investment_models_paths:
            if investment_models.exists():
                content = investment_models.read_text(encoding="utf-8")
                
                # Vérifier qu'aucun modèle ne force l'activation (hors commentaires)
                # Ignorer les commentaires (lignes commençant par # ou contenant # avant le code)
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    # Ignorer les commentaires
                    if line.strip().startswith('#') or '#' in line and line.split('#')[0].strip() == '':
                        continue
                    # Vérifier si la ligne force l'activation (hors commentaires)
                    if re.search(r'enable.*investment.*=.*true', line, re.IGNORECASE):
                        violations.append(
                            f"{investment_models.relative_to(backend_dir.parent)}:{line_num} : "
                            "Un modèle force l'activation d'ENABLE_INVESTMENT_FEATURES. "
                            "C'est une violation de la constitution EGOEJO. "
                            f"Ligne: {line.strip()}"
                        )
                        all_checks_passed = False
        
        # 5. Vérifier que le setting est bien False par défaut dans l'environnement de test
        if hasattr(settings, 'ENABLE_INVESTMENT_FEATURES'):
            if settings.ENABLE_INVESTMENT_FEATURES:
                violations.append(
                    "ENVIRONNEMENT : ENABLE_INVESTMENT_FEATURES est True dans l'environnement de test. "
                    "V2.0 ne doit PAS être activé par défaut. "
                    "Le test DOIT échouer si V2.0 est activé sans contrôle explicite."
                )
                all_checks_passed = False
        
        # Générer le rapport d'échec
        if not all_checks_passed:
            report = [
                "=" * 80,
                "VIOLATION DE LA CONSTITUTION EGOEJO : V2.0 peut être activée sans feature flag",
                "=" * 80,
                "",
                "RÈGLE ABSOLUE : V2.0 (Investment) DOIT être strictement contrôlé par ENABLE_INVESTMENT_FEATURES.",
                "Aucun assouplissement temporaire n'est autorisé.",
                "",
                f"Nombre de violations : {len(violations)}",
                "",
                "Violations détectées :",
                "-" * 80,
            ]
            
            for i, violation in enumerate(violations, 1):
                report.append(f"{i}. {violation}")
            
            report.extend([
                "",
                "=" * 80,
                "ACTION REQUISE :",
                "1. Vérifier que ENABLE_INVESTMENT_FEATURES est défini dans settings.py",
                "2. Vérifier que la valeur par défaut est False",
                "3. Vérifier que TOUS les points d'entrée V2.0 vérifient le flag",
                "4. Vérifier qu'aucun code ne force l'activation du flag",
                "5. Le pipeline CI DOIT échouer si ce test échoue",
                "=" * 80,
            ])
            
            pytest.fail("\n".join(report))
    
    def test_aucun_contournement_feature_flag(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une feature financière contourne un feature flag.
        
        Test : Vérifier qu'aucun code ne contourne les vérifications de feature flag.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        
        # Patterns suspects de contournement
        suspicious_patterns = [
            r"#.*bypass.*feature.*flag",
            r"#.*ignore.*ENABLE_INVESTMENT",
            r"if.*True.*#.*force.*enable",
            r"ENABLE_INVESTMENT.*=.*True.*#.*override",
        ]
        
        violations = []
        
        # Scanner tous les fichiers Python du backend
        for py_file in backend_dir.rglob("*.py"):
            # Ignorer les tests et migrations
            if "test" in str(py_file) or "migration" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                for pattern in suspicious_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        violations.append({
                            "file": str(py_file.relative_to(backend_dir.parent)),
                            "line": content[:match.start()].count("\n") + 1,
                            "match": match.group(0)[:50],
                        })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} contournement(s) de feature flag détecté(s).\n"
            f"Les feature flags doivent être respectés pour protéger la gouvernance.\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )
    
    def test_feature_flag_verifie_dans_services(self):
        """
        VIOLATION DE LA CONSTITUTION EGOEJO si :
        Les services financiers ne vérifient pas le feature flag.
        
        RÈGLE ABSOLUE : Tous les services V2.0 DOIVENT vérifier ENABLE_INVESTMENT_FEATURES.
        Aucun assouplissement temporaire n'est autorisé.
        
        Test : Vérifier que les services investment vérifient ENABLE_INVESTMENT_FEATURES.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        finance_services = backend_dir / "finance" / "services.py"
        
        if not finance_services.exists():
            pytest.fail(
                "VIOLATION CONSTITUTION EGOEJO : "
                "Le fichier finance/services.py est introuvable. "
                "Ce fichier est critique pour la gouvernance V2.0. "
                "Le test DOIT échouer si le fichier n'existe pas."
            )
        
        content = finance_services.read_text(encoding="utf-8")
        
        # Vérifier que les fonctions investment publiques vérifient le feature flag
        # Note: _calculate_equity_amount est une fonction privée (préfixe _) appelée par create_equity_pledge
        # qui vérifie déjà le feature flag via _validate_pledge_request, donc on ne vérifie que les fonctions publiques
        investment_functions = [
            "create_equity_pledge",
            "process_equity_investment",
        ]
        
        violations = []
        
        for func_name in investment_functions:
            if func_name in content:
                # Vérifier que la fonction vérifie le feature flag
                # Chercher dans un rayon de 100 lignes après la définition de la fonction
                func_def_pattern = re.compile(
                    rf"def\s+{func_name}\s*\(",
                    re.IGNORECASE
                )
                func_match = func_def_pattern.search(content)
                
                if func_match:
                    # Extraire les 100 lignes suivantes (environ 3000 caractères)
                    start_pos = func_match.end()
                    lines_after = content[start_pos:start_pos + 3000]
                    
                    # Vérifier la présence de vérification de feature flag
                    # _validate_pledge_request vérifie le flag pour EQUITY
                    has_flag_check = (
                        "ENABLE_INVESTMENT" in lines_after or
                        "IsInvestmentFeatureEnabled" in lines_after or
                        "_validate_pledge_request" in lines_after  # Cette fonction vérifie le flag
                    )
                    
                    if not has_flag_check:
                        violations.append(func_name)
        
        if violations:
            pytest.fail(
                f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} fonction(s) investment ne vérifie(nt) pas le feature flag.\n"
                f"Les fonctions investment doivent vérifier ENABLE_INVESTMENT_FEATURES.\n\n"
                f"Violations détectées :\n" +
                "\n".join([f"  - {v}" for v in violations])
            )

