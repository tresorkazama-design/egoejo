"""
EGOEJO Compliance Test : Meta-Compliance - Vérification des Tags

LOI EGOEJO :
"Tous les tests de compliance DOIVENT être tagués avec @pytest.mark.egoejo_compliance
pour être exécutés dans la CI et garantir la conformité."

Ce test vérifie que :
- Tous les fichiers de test dans backend/tests/compliance/ sont tagués
- Aucun test de compliance n'est ignoré par la CI

Violation du Manifeste EGOEJO si :
- Un fichier de test de compliance n'est pas tagué @egoejo_compliance
- Un test de compliance peut être ignoré par la CI
"""
import pytest
from pathlib import Path
import ast
import re


@pytest.mark.egoejo_compliance
class TestMetaCompliance:
    """
    Tests de conformité : Meta-Compliance - Vérification des Tags
    
    RÈGLE ABSOLUE : Tous les tests de compliance doivent être tagués @egoejo_compliance.
    """
    
    def test_tous_les_tests_compliance_sont_tagues(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un fichier de test de compliance n'est pas tagué @egoejo_compliance.
        
        Test : Scanner tous les fichiers .py dans backend/tests/compliance/ et vérifier
        qu'ils contiennent le marqueur @pytest.mark.egoejo_compliance.
        """
        # Chemin vers le dossier compliance
        compliance_dir = Path(__file__).parent
        
        # Fichiers à exclure
        excluded_files = {
            '__init__.py',
            'conftest.py',
            'test_meta_compliance.py',  # Ce fichier lui-même
        }
        
        # Pattern pour détecter le marqueur
        marker_patterns = [
            r'@pytest\.mark\.egoejo_compliance',
            r'@egoejo_compliance',  # Format court possible
            r'pytest\.mark\.egoejo_compliance',
        ]
        
        violations = []
        
        # Scanner récursivement tous les fichiers .py
        for test_file in compliance_dir.rglob('*.py'):
            # Ignorer les fichiers exclus
            if test_file.name in excluded_files:
                continue
            
            # Ignorer les fichiers dans __pycache__
            if '__pycache__' in test_file.parts:
                continue
            
            # Lire le contenu du fichier
            try:
                content = test_file.read_text(encoding='utf-8')
            except Exception as e:
                violations.append(
                    f"Impossible de lire {test_file.relative_to(compliance_dir.parent.parent)} : {e}"
                )
                continue
            
            # Vérifier si le fichier contient au moins un marqueur
            has_marker = any(
                re.search(pattern, content, re.MULTILINE)
                for pattern in marker_patterns
            )
            
            if not has_marker:
                # Vérifier si le fichier contient des tests (classe Test* ou fonction test_*)
                has_tests = (
                    'class Test' in content or
                    'def test_' in content or
                    '@pytest.mark' in content
                )
                
                # Si le fichier contient des tests mais pas le marqueur, c'est une violation
                if has_tests:
                    relative_path = test_file.relative_to(compliance_dir.parent.parent)
                    violations.append(
                        f"Le fichier de test {relative_path} n'est pas tagué @egoejo_compliance "
                        f"et risque d'être ignoré par la CI."
                    )
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} fichier(s) de test de compliance "
            f"non tagué(s) @egoejo_compliance.\n\n"
            f"Les fichiers suivants doivent être tagués pour être exécutés dans la CI :\n" +
            "\n".join([f"  - {v}" for v in violations]) +
            "\n\n"
            f"ACTION REQUISE : Ajouter @pytest.mark.egoejo_compliance à chaque classe de test "
            f"ou utiliser pytestmark = pytest.mark.egoejo_compliance au niveau du module."
        )
    
    def test_aucun_test_compliance_dans_sous_dossiers_non_tague(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un test de compliance dans un sous-dossier n'est pas tagué.
        
        Test : Vérifier spécifiquement les sous-dossiers (philosophy, structure, governance, finance).
        """
        compliance_dir = Path(__file__).parent
        
        # Sous-dossiers à vérifier
        subdirs = ['philosophy', 'structure', 'governance', 'finance']
        
        violations = []
        
        for subdir_name in subdirs:
            subdir = compliance_dir / subdir_name
            if not subdir.exists():
                continue
            
            # Scanner tous les fichiers .py dans le sous-dossier
            for test_file in subdir.rglob('*.py'):
                # Ignorer __init__.py et __pycache__
                if test_file.name in ['__init__.py', 'conftest.py']:
                    continue
                
                if '__pycache__' in test_file.parts:
                    continue
                
                # Lire le contenu
                try:
                    content = test_file.read_text(encoding='utf-8')
                except Exception:
                    continue
                
                # Vérifier la présence du marqueur
                has_marker = re.search(
                    r'@pytest\.mark\.egoejo_compliance|@egoejo_compliance|pytestmark.*egoejo_compliance',
                    content,
                    re.MULTILINE | re.IGNORECASE
                )
                
                # Vérifier si le fichier contient des tests
                has_tests = (
                    'class Test' in content or
                    'def test_' in content
                )
                
                if has_tests and not has_marker:
                    relative_path = test_file.relative_to(compliance_dir.parent.parent)
                    violations.append(
                        f"Le fichier de test {relative_path} dans le sous-dossier '{subdir_name}' "
                        f"n'est pas tagué @egoejo_compliance et risque d'être ignoré par la CI."
                    )
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} fichier(s) de test dans les sous-dossiers "
            f"non tagué(s) @egoejo_compliance.\n\n"
            f"Violations détectées :\n" +
            "\n".join([f"  - {v}" for v in violations]) +
            "\n\n"
            f"ACTION REQUISE : Ajouter @pytest.mark.egoejo_compliance à chaque classe de test."
        )

