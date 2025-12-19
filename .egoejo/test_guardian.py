#!/usr/bin/env python3
"""
Tests pour le Guardian EGOEJO

Ce script teste les fonctionnalités du Guardian avec des exemples de violations.
"""
import sys
import tempfile
from pathlib import Path

# Ajouter le répertoire .egoejo au path pour importer guardian
guardian_dir = Path(__file__).parent
sys.path.insert(0, str(guardian_dir))

# Import direct depuis le fichier
import importlib.util
spec = importlib.util.spec_from_file_location("guardian", guardian_dir / "guardian.py")
guardian_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardian_module)

EGOEJOGuardian = guardian_module.EGOEJOGuardian
Verdict = guardian_module.Verdict
Severity = guardian_module.Severity


def test_no_conversion_violation():
    """Test : Détection d'une violation de conversion SAKA ↔ EUR"""
    print("🧪 Test 1 : Détection conversion SAKA ↔ EUR")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    # Diff simulé avec violation
    diff_content = """
+def convert_saka_to_eur(saka_amount):
+    return saka_amount * 0.01  # 1 SAKA = 0.01 EUR
"""
    
    violations = guardian.analyze_diff(diff_content, "backend/core/services/saka.py")
    
    assert len(violations) > 0, "Devrait détecter une violation de conversion"
    assert any(v.rule == 'no_conversion' for v in violations), "Devrait détecter la règle 'no_conversion'"
    assert any(v.severity == Severity.CRITICAL for v in violations), "Devrait être CRITICAL"
    
    print("✅ Violation détectée :", violations[0].description)
    return True


def test_no_financial_return_violation():
    """Test : Détection d'un rendement financier basé sur SAKA"""
    print("\n🧪 Test 2 : Détection rendement financier SAKA")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    diff_content = """
+def calculate_saka_interest(wallet, rate):
+    return wallet.balance * rate
"""
    
    violations = guardian.analyze_diff(diff_content, "backend/core/services/saka.py")
    
    assert len(violations) > 0, "Devrait détecter une violation de rendement"
    assert any('interest' in v.description.lower() for v in violations), "Devrait détecter 'interest'"
    
    print("✅ Violation détectée :", violations[0].description)
    return True


def test_saka_cycle_violation():
    """Test : Détection d'une tentative de désactiver le compostage"""
    print("\n🧪 Test 3 : Détection violation cycle SAKA (compostage)")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    diff_content = """
+if user.is_premium:
+    skip_compost = True  # Les utilisateurs premium ne compostent pas
"""
    
    violations = guardian.analyze_diff(diff_content, "backend/core/services/saka.py")
    
    assert len(violations) > 0, "Devrait détecter une violation du cycle SAKA"
    assert any('compost' in v.description.lower() for v in violations), "Devrait détecter 'compost'"
    assert any(v.severity == Severity.CRITICAL for v in violations), "Devrait être CRITICAL"
    
    print("✅ Violation détectée :", violations[0].description)
    return True


def test_compatible_pr():
    """Test : PR compatible (pas de violations)"""
    print("\n🧪 Test 4 : PR compatible")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    # Diff simulé sans violation
    diff_content = """
+def harvest_saka(user, amount, reason):
+    wallet, _ = SakaWallet.objects.get_or_create(user=user)
+    wallet.balance += amount
+    wallet.total_harvested += amount
+    wallet.save()
"""
    
    violations = guardian.analyze_diff(diff_content, "backend/core/services/saka.py")
    
    # Ne devrait pas avoir de violations critiques
    critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
    assert len(critical_violations) == 0, "Ne devrait pas avoir de violations critiques"
    
    print("✅ Aucune violation critique détectée")
    return True


def test_file_classification():
    """Test : Classification des fichiers SAKA vs EUR"""
    print("\n🧪 Test 5 : Classification des fichiers")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    # Test fichiers SAKA
    saka_files = [
        "backend/core/services/saka.py",
        "backend/core/models/saka.py",
        "frontend/src/components/SakaBalance.jsx"
    ]
    
    for file_path in saka_files:
        file_type = guardian.classify_file(file_path)
        assert file_type == 'saka', f"Devrait classifier {file_path} comme SAKA"
        print(f"✅ {file_path} → SAKA")
    
    # Test fichiers EUR
    eur_files = [
        "backend/finance/services.py",
        "backend/investment/models.py",
        "frontend/src/components/FinanceDashboard.jsx"
    ]
    
    for file_path in eur_files:
        file_type = guardian.classify_file(file_path)
        assert file_type == 'eur', f"Devrait classifier {file_path} comme EUR"
        print(f"✅ {file_path} → EUR")
    
    return True


def test_missing_tests_detection():
    """Test : Détection de tests manquants pour changements SAKA"""
    print("\n🧪 Test 6 : Détection tests manquants")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    modified_files = [
        "backend/core/services/saka.py",  # Fichier SAKA modifié
        "backend/core/models/saka.py",     # Fichier SAKA modifié
    ]
    
    test_files = []  # Aucun test modifié
    
    missing_tests = guardian.check_tests_for_saka_changes(modified_files, test_files)
    
    assert len(missing_tests) > 0, "Devrait détecter des tests manquants"
    print(f"✅ Tests manquants détectés : {missing_tests}")
    
    return True


def test_full_analysis():
    """Test : Analyse complète d'une PR"""
    print("\n🧪 Test 7 : Analyse complète d'une PR")
    
    config_path = Path(__file__).parent / "guardian.yml"
    guardian = EGOEJOGuardian(config_path=str(config_path))
    
    # Diff avec violations
    diff_content = """
+def convert_saka_to_eur(saka_amount):
+    return saka_amount * 0.01
+
+def disable_compost_for_premium():
+    skip_compost = True
"""
    
    modified_files = [
        "backend/core/services/saka.py",
    ]
    
    result = guardian.analyze_pr(diff_content, modified_files)
    
    assert result.verdict == Verdict.NON_COMPATIBLE, "Devrait être NON COMPATIBLE"
    assert len(result.violations) > 0, "Devrait avoir des violations"
    
    print(f"✅ Verdict : {result.verdict.value}")
    print(f"✅ Violations : {len(result.violations)}")
    
    return True


def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("🧪 Tests du Guardian EGOEJO")
    print("=" * 60)
    
    tests = [
        test_no_conversion_violation,
        test_no_financial_return_violation,
        test_saka_cycle_violation,
        test_compatible_pr,
        test_file_classification,
        test_missing_tests_detection,
        test_full_analysis,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Échec : {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Erreur : {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Résultats : {passed} réussis, {failed} échoués")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ Tous les tests sont passés !")
        sys.exit(0)


if __name__ == '__main__':
    main()

