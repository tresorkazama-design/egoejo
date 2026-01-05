#!/usr/bin/env python3
"""
Tests unitaires pour le bot EGOEJO PR Bot.

Simule des PRs fautives pour vérifier la détection des violations.
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au path pour importer le bot
sys.path.insert(0, str(Path(__file__).parent.parent))

from egoejo_pr_bot import EGOEJOPRBot, ComplianceLevel, Risk


def create_test_repo():
    """
    Crée un dépôt Git temporaire pour les tests.
    
    Returns:
        Chemin du dépôt temporaire
    """
    repo_path = tempfile.mkdtemp()
    
    # Initialiser le dépôt Git
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Bot"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@egoejo.test"], cwd=repo_path, check=True, capture_output=True)
    
    # Créer un fichier initial
    initial_file = Path(repo_path) / "README.md"
    initial_file.write_text("# EGOEJO Test Repo\n", encoding="utf-8")
    
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
    
    return repo_path


def create_test_branch(repo_path: str, branch_name: str, files_content: dict):
    """
    Crée une branche de test avec des fichiers.
    
    Args:
        repo_path: Chemin du dépôt
        branch_name: Nom de la branche
        files_content: Dictionnaire {nom_fichier: contenu}
    """
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True, capture_output=True)
    
    for filename, content in files_content.items():
        file_path = Path(repo_path) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", filename], cwd=repo_path, check=True, capture_output=True)
    
    subprocess.run(["git", "commit", "-m", f"Test commit: {branch_name}"], cwd=repo_path, check=True, capture_output=True)


def test_pr_with_saka_eur_conversion():
    """
    Test: PR avec conversion SAKA ↔ EUR (violation critique).
    """
    print("🧪 Test 1: PR avec conversion SAKA ↔ EUR")
    
    repo_path = create_test_repo()
    
    # Créer une branche avec violation
    create_test_branch(repo_path, "feature/saka-conversion", {
        "backend/core/services/saka.py": """
def convert_saka_to_eur(amount_saka):
    exchange_rate = 0.01
    return amount_saka * exchange_rate
"""
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/saka-conversion"
    
    analysis = bot.analyze_pr()
    
    assert analysis.compliance_level == ComplianceLevel.NON_COMPATIBLE, \
        f"Attendu NON_COMPATIBLE, reçu {analysis.compliance_level}"
    assert analysis.blocking is True, "La PR devrait être bloquante"
    assert len(analysis.philosophical_risks) > 0, "Devrait détecter des risques philosophiques"
    assert any("conversion" in r.description.lower() for r in analysis.philosophical_risks), \
        "Devrait détecter une violation de conversion"
    
    print("✅ Test 1 réussi: Conversion SAKA ↔ EUR détectée\n")


def test_pr_with_monetary_display():
    """
    Test: PR avec affichage monétaire SAKA (violation critique).
    """
    print("🧪 Test 2: PR avec affichage monétaire SAKA")
    
    repo_path = create_test_repo()
    
    create_test_branch(repo_path, "feature/monetary-display", {
        "frontend/src/components/SakaBalance.jsx": """
const SakaBalance = ({ balance }) => {
    return <div>Votre solde SAKA: {balance} €</div>;
};
"""
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/monetary-display"
    
    analysis = bot.analyze_pr()
    
    assert analysis.compliance_level == ComplianceLevel.NON_COMPATIBLE, \
        f"Attendu NON_COMPATIBLE, reçu {analysis.compliance_level}"
    assert analysis.blocking is True, "La PR devrait être bloquante"
    assert len(analysis.philosophical_risks) > 0, "Devrait détecter des risques philosophiques"
    
    print("✅ Test 2 réussi: Affichage monétaire détecté\n")


def test_pr_with_compost_disabled():
    """
    Test: PR désactivant le compostage (violation critique).
    """
    print("🧪 Test 3: PR désactivant le compostage")
    
    repo_path = create_test_repo()
    
    create_test_branch(repo_path, "feature/disable-compost", {
        "backend/config/settings.py": """
SAKA_COMPOST_ENABLED = False
SAKA_COMPOST_RATE = 0
"""
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/disable-compost"
    
    analysis = bot.analyze_pr()
    
    assert analysis.compliance_level == ComplianceLevel.NON_COMPATIBLE, \
        f"Attendu NON_COMPATIBLE, reçu {analysis.compliance_level}"
    assert analysis.blocking is True, "La PR devrait être bloquante"
    assert len(analysis.philosophical_risks) > 0, "Devrait détecter des risques philosophiques"
    
    print("✅ Test 3 réussi: Désactivation du compostage détectée\n")


def test_pr_with_investment_activation():
    """
    Test: PR activant V2.0 sans contrôle (violation critique).
    """
    print("🧪 Test 4: PR activant V2.0 sans contrôle")
    
    repo_path = create_test_repo()
    
    create_test_branch(repo_path, "feature/activate-v2", {
        "backend/config/settings.py": """
ENABLE_INVESTMENT_FEATURES = True
"""
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/activate-v2"
    
    analysis = bot.analyze_pr()
    
    assert analysis.compliance_level == ComplianceLevel.NON_COMPATIBLE, \
        f"Attendu NON_COMPATIBLE, reçu {analysis.compliance_level}"
    assert analysis.blocking is True, "La PR devrait être bloquante"
    assert len(analysis.philosophical_risks) > 0, "Devrait détecter des risques philosophiques"
    
    print("✅ Test 4 réussi: Activation V2.0 sans contrôle détectée\n")


def test_pr_with_test_removal():
    """
    Test: PR supprimant des tests de compliance (violation critique).
    """
    print("🧪 Test 5: PR supprimant des tests de compliance")
    
    repo_path = create_test_repo()
    
    # Créer un test de compliance initial
    test_file = Path(repo_path) / "backend/tests/compliance/test_saka.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
@pytest.mark.egoejo_compliance
def test_no_saka_eur_conversion():
    assert True
""", encoding="utf-8")
    
    subprocess.run(["git", "add", "backend/tests/compliance/test_saka.py"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add compliance test"], cwd=repo_path, check=True, capture_output=True)
    
    # Créer une branche qui supprime le test
    create_test_branch(repo_path, "feature/remove-test", {
        "backend/tests/compliance/test_saka.py": ""  # Fichier vide = suppression
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/remove-test"
    
    analysis = bot.analyze_pr()
    
    # La suppression de test devrait être détectée
    assert len(analysis.philosophical_risks) > 0 or len(analysis.technical_risks) > 0, \
        "Devrait détecter la suppression de test"
    
    print("✅ Test 5 réussi: Suppression de test détectée\n")


def test_pr_with_direct_wallet_modification():
    """
    Test: PR modifiant directement le wallet (risque technique).
    """
    print("🧪 Test 6: PR modifiant directement le wallet")
    
    repo_path = create_test_repo()
    
    create_test_branch(repo_path, "feature/direct-wallet", {
        "backend/core/admin.py": """
wallet.balance = 1000
wallet.save()
"""
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/direct-wallet"
    
    analysis = bot.analyze_pr()
    
    assert len(analysis.technical_risks) > 0, "Devrait détecter des risques techniques"
    assert analysis.compliance_level in [ComplianceLevel.COMPATIBLE_CONDITIONS, ComplianceLevel.NON_COMPATIBLE], \
        f"Attendu COMPATIBLE_CONDITIONS ou NON_COMPATIBLE, reçu {analysis.compliance_level}"
    
    print("✅ Test 6 réussi: Modification directe du wallet détectée\n")


def test_pr_compliant():
    """
    Test: PR conforme (aucune violation).
    """
    print("🧪 Test 7: PR conforme")
    
    repo_path = create_test_repo()
    
    create_test_branch(repo_path, "feature/compliant", {
        "backend/core/services/saka.py": """
def harvest_saka(user, reason, amount):
    # Fonction conforme
    wallet = get_or_create_wallet(user)
    wallet.balance += amount
    wallet.save()
"""
    })
    
    bot = EGOEJOPRBot(repo_path=repo_path)
    bot.base_ref = "main"
    bot.head_ref = "feature/compliant"
    
    analysis = bot.analyze_pr()
    
    assert analysis.compliance_level == ComplianceLevel.COMPATIBLE, \
        f"Attendu COMPATIBLE, reçu {analysis.compliance_level}"
    assert analysis.blocking is False, "La PR ne devrait pas être bloquante"
    assert len(analysis.philosophical_risks) == 0, "Ne devrait pas détecter de risques philosophiques"
    
    print("✅ Test 7 réussi: PR conforme détectée\n")


def run_all_tests():
    """Exécute tous les tests"""
    print("=" * 80)
    print("🧪 Tests EGOEJO PR Bot - Simulation de PRs fautives")
    print("=" * 80)
    print()
    
    tests = [
        test_pr_with_saka_eur_conversion,
        test_pr_with_monetary_display,
        test_pr_with_compost_disabled,
        test_pr_with_investment_activation,
        test_pr_with_test_removal,
        test_pr_with_direct_wallet_modification,
        test_pr_compliant,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__} échoué: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} erreur: {e}\n")
            failed += 1
    
    print("=" * 80)
    print(f"📊 Résultats: {passed} réussis, {failed} échoués")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

