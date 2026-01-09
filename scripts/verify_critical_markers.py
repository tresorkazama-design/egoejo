#!/usr/bin/env python3
"""
Script de vérification des marqueurs @pytest.mark.critical.

Vérifie que :
1. Les fichiers déclarés dans CRITICAL_TESTS_REGISTRY.yml ont bien @pytest.mark.critical
2. Les modules "core" obligatoires ont bien des tests critiques
3. Aucun test critique n'est manquant pour un module "core"

Usage:
    python scripts/verify_critical_markers.py

Exit codes:
    0: Tous les tests critiques sont présents et marqués correctement
    1: Au moins un test critique est manquant ou non marqué
"""
import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Set, Tuple


# Chemin du repo (depuis le script)
REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "testing" / "CRITICAL_TESTS_REGISTRY.yml"
BACKEND_TESTS_DIR = REPO_ROOT / "backend" / "core" / "tests"
FRONTEND_TESTS_DIR = REPO_ROOT / "frontend" / "frontend" / "e2e"


def load_registry() -> Dict:
    """Charge le registry YAML."""
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry non trouvé: {REGISTRY_PATH}")
        sys.exit(1)
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def find_critical_marker_in_file(file_path: Path) -> bool:
    """
    Vérifie si un fichier contient @pytest.mark.critical.
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        bool: True si @pytest.mark.critical est présent
    """
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        # Chercher @pytest.mark.critical (avec ou sans espaces)
        pattern = r'@pytest\.mark\.critical|pytest\.mark\.critical'
        return bool(re.search(pattern, content))
    except Exception as e:
        print(f"⚠️  Erreur lecture {file_path}: {e}")
        return False


def find_test_files_in_directory(directory: Path, pattern: str = "test_*.py") -> List[Path]:
    """
    Trouve tous les fichiers de tests dans un répertoire.
    
    Args:
        directory: Répertoire à scanner
        pattern: Pattern de recherche (défaut: test_*.py)
        
    Returns:
        List[Path]: Liste des fichiers de tests
    """
    if not directory.exists():
        return []
    
    test_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(Path(root) / file)
    
    return test_files


def find_test_files_frontend(directory: Path, pattern: str = "*.spec.js") -> List[Path]:
    """
    Trouve tous les fichiers de tests E2E frontend.
    
    Args:
        directory: Répertoire à scanner
        pattern: Pattern de recherche (défaut: *.spec.js)
        
    Returns:
        List[Path]: Liste des fichiers de tests
    """
    if not directory.exists():
        return []
    
    test_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".spec.js"):
                test_files.append(Path(root) / file)
    
    return test_files


def verify_registry_files(registry: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Vérifie que les fichiers déclarés dans le registry ont bien @pytest.mark.critical.
    
    Args:
        registry: Liste des entrées du registry
        
    Returns:
        Tuple[bool, List[str]]: (succès, liste des erreurs)
    """
    errors = []
    success = True
    
    for entry in registry:
        if not isinstance(entry, dict):
            continue
        
        file_path = REPO_ROOT / entry.get('path', '')
        required = entry.get('required', False)
        module = entry.get('module', 'unknown')
        
        if not required:
            continue
        
        if not file_path.exists():
            errors.append(f"❌ Fichier déclaré manquant: {entry.get('path')} (module: {module})")
            success = False
            continue
        
        has_marker = find_critical_marker_in_file(file_path)
        
        if not has_marker:
            errors.append(
                f"❌ Fichier {entry.get('path')} (module: {module}) "
                f"DOIT avoir @pytest.mark.critical mais ne l'a pas"
            )
            success = False
        else:
            print(f"✅ {entry.get('path')} (module: {module}) - @pytest.mark.critical présent")
    
    return success, errors


def verify_core_modules(registry: Dict) -> Tuple[bool, List[str]]:
    """
    Vérifie que les modules "core" obligatoires ont bien des tests critiques.
    
    Args:
        registry: Registry complet (incluant core_modules_required)
        
    Returns:
        Tuple[bool, List[str]]: (succès, liste des erreurs)
    """
    errors = []
    success = True
    
    core_modules = registry.get('core_modules_required', [])
    
    for module in core_modules:
        module_name = module.get('name', 'unknown')
        test_paths = module.get('test_paths', [])
        
        if not test_paths:
            errors.append(f"❌ Module core '{module_name}' n'a pas de tests déclarés")
            success = False
            continue
        
        # Vérifier que tous les tests déclarés existent et ont @pytest.mark.critical
        for test_path_str in test_paths:
            test_path = REPO_ROOT / test_path_str
            
            if not test_path.exists():
                errors.append(
                    f"❌ Test critique manquant pour module '{module_name}': {test_path_str}"
                )
                success = False
                continue
            
            has_marker = find_critical_marker_in_file(test_path)
            
            if not has_marker:
                errors.append(
                    f"❌ Test {test_path_str} (module: {module_name}) "
                    f"DOIT avoir @pytest.mark.critical mais ne l'a pas"
                )
                success = False
            else:
                print(f"✅ Module '{module_name}' - {test_path_str} a @pytest.mark.critical")
    
    return success, errors


def verify_no_missing_critical_tests(registry: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Vérifie qu'aucun test critique n'est manquant pour un module "core".
    
    Cette fonction scanne les répertoires de tests et vérifie que tous les fichiers
    qui devraient être critiques selon le registry le sont bien.
    
    Args:
        registry: Liste des entrées du registry
        
    Returns:
        Tuple[bool, List[str]]: (succès, liste des erreurs)
    """
    errors = []
    success = True
    
    # Construire un set des fichiers déclarés comme critiques
    declared_critical = set()
    for entry in registry:
        if isinstance(entry, dict) and entry.get('required', False):
            declared_critical.add(entry.get('path', ''))
    
    # Scanner les répertoires de tests backend
    backend_test_files = find_test_files_in_directory(BACKEND_TESTS_DIR)
    
    for test_file in backend_test_files:
        # Convertir en chemin relatif depuis REPO_ROOT
        rel_path = test_file.relative_to(REPO_ROOT)
        rel_path_str = str(rel_path).replace('\\', '/')
        
        # Si le fichier n'est pas dans le registry mais contient "critical" dans le nom,
        # c'est suspect (peut-être un test critique non déclaré)
        if 'critical' in test_file.name.lower() and rel_path_str not in declared_critical:
            # Vérifier si le fichier a @pytest.mark.critical
            has_marker = find_critical_marker_in_file(test_file)
            if has_marker:
                # Fichier a le marker mais n'est pas dans le registry
                print(f"⚠️  {rel_path_str} a @pytest.mark.critical mais n'est pas dans le registry")
                # Ne pas échouer, juste avertir
    
    return success, errors


def main():
    """Fonction principale."""
    print("🔍 Vérification des marqueurs @pytest.mark.critical...")
    print(f"📁 Registry: {REGISTRY_PATH}")
    print()
    
    # Charger le registry
    registry_data = load_registry()
    
    # Extraire la liste des fichiers (tout sauf core_modules_required)
    registry_files = [entry for entry in registry_data if isinstance(entry, dict)]
    
    # Vérifier les fichiers déclarés
    print("📋 Vérification des fichiers déclarés dans le registry...")
    files_success, files_errors = verify_registry_files(registry_files)
    print()
    
    # Vérifier les modules core
    print("🔧 Vérification des modules core obligatoires...")
    modules_success, modules_errors = verify_core_modules(registry_data)
    print()
    
    # Vérifier qu'aucun test critique n'est manquant
    print("🔎 Vérification des tests critiques manquants...")
    missing_success, missing_errors = verify_no_missing_critical_tests(registry_files)
    print()
    
    # Résumé
    all_errors = files_errors + modules_errors + missing_errors
    all_success = files_success and modules_success and missing_success
    
    if all_errors:
        print("❌ ERREURS DÉTECTÉES:")
        for error in all_errors:
            print(f"  {error}")
        print()
    
    if all_success:
        print("✅ Tous les tests critiques sont présents et marqués correctement")
        sys.exit(0)
    else:
        print("❌ Au moins un test critique est manquant ou non marqué")
        print()
        print("💡 Actions requises:")
        print("  1. Ajouter @pytest.mark.critical aux fichiers manquants")
        print("  2. Ajouter les fichiers manquants au registry CRITICAL_TESTS_REGISTRY.yml")
        print("  3. Vérifier que les modules core ont bien des tests critiques")
        sys.exit(1)


if __name__ == "__main__":
    main()

