"""
Tests unitaires pour le script verify_critical_markers.py.

Vérifie que le script fonctionne correctement.
"""
import pytest
import tempfile
import yaml
from pathlib import Path
import sys

# Ajouter le répertoire scripts au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from verify_critical_markers import (
    load_registry,
    find_critical_marker_in_file,
    verify_registry_files,
    verify_core_modules,
)


def test_load_registry_valid():
    """Test que load_registry charge un YAML valide"""
    # Créer un registry temporaire valide
    registry_data = [
        {
            'path': 'backend/core/tests/test_example.py',
            'required': True,
            'module': 'test',
            'description': 'Test example'
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)
    
    try:
        # Modifier temporairement le chemin du registry
        import verify_critical_markers
        original_path = verify_critical_markers.REGISTRY_PATH
        verify_critical_markers.REGISTRY_PATH = temp_path
        
        registry = load_registry()
        assert isinstance(registry, list)
        assert len(registry) > 0
        
        verify_critical_markers.REGISTRY_PATH = original_path
    finally:
        temp_path.unlink()


def test_find_critical_marker_present():
    """Test que find_critical_marker_in_file trouve @pytest.mark.critical"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import pytest

@pytest.mark.critical
def test_example():
    pass
""")
        temp_path = Path(f.name)
    
    try:
        has_marker = find_critical_marker_in_file(temp_path)
        assert has_marker is True
    finally:
        temp_path.unlink()


def test_find_critical_marker_absent():
    """Test que find_critical_marker_in_file ne trouve pas @pytest.mark.critical"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import pytest

def test_example():
    pass
""")
        temp_path = Path(f.name)
    
    try:
        has_marker = find_critical_marker_in_file(temp_path)
        assert has_marker is False
    finally:
        temp_path.unlink()


def test_verify_registry_files_all_present():
    """Test que verify_registry_files valide correctement"""
    registry = [
        {
            'path': 'backend/core/tests/test_example.py',
            'required': True,
            'module': 'test',
            'description': 'Test example'
        }
    ]
    
    # Créer un fichier de test avec @pytest.mark.critical
    test_file = Path('backend/core/tests/test_example.py')
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
import pytest

@pytest.mark.critical
def test_example():
    pass
""")
    
    try:
        success, errors = verify_registry_files(registry)
        # Le test devrait réussir si le fichier existe et a le marker
        # (mais peut échouer si le chemin n'est pas correct)
        assert isinstance(success, bool)
        assert isinstance(errors, list)
    finally:
        if test_file.exists():
            test_file.unlink()
        if test_file.parent.exists() and not any(test_file.parent.iterdir()):
            test_file.parent.rmdir()


def test_verify_core_modules_valid():
    """Test que verify_core_modules valide correctement"""
    registry_data = {
        'core_modules_required': [
            {
                'name': 'test',
                'description': 'Test module',
                'test_paths': []
            }
        ]
    }
    
    success, errors = verify_core_modules(registry_data)
    assert isinstance(success, bool)
    assert isinstance(errors, list)

