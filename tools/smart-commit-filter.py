#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Commit Filter - Guardian Check pour commits sûrs
Filtre les fichiers dangereux avant commit
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Patterns de détection de secrets
SECRET_PATTERNS = [
    r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
    r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
    r'password\s*=\s*["\'][^"\']+["\']',
    r'token\s*=\s*["\'][^"\']{20,}["\']',  # Tokens longs
    r'private[_-]?key\s*=\s*["\'][^"\']+["\']',
    r'access[_-]?token\s*=\s*["\'][^"\']+["\']',
    r'aws[_-]?secret[_-]?access[_-]?key',
    r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
]

# Fichiers temporaires/système à exclure
EXCLUDED_PATTERNS = [
    r'\.DS_Store$',
    r'__pycache__',
    r'\.pyc$',
    r'\.pyo$',
    r'\.log$',
    r'\.tmp$',
    r'\.swp$',
    r'\.swo$',
    r'\.bak$',
    r'\.orig$',
    r'node_modules',
    r'\.venv',
    r'venv/',
    r'htmlcov/',
    r'\.pytest_cache',
    r'\.coverage',
    r'\.env$',
    r'\.env\.local$',
    r'\.env\.production$',
]

# Patterns de code dangereux (désactivation SAKA)
DANGEROUS_CODE_PATTERNS = [
    (r'ENABLE_SAKA\s*=\s*False', 'Désactivation SAKA hardcodée'),
    (r'SAKA_COMPOST_ENABLED\s*=\s*False', 'Désactivation compostage hardcodée'),
    (r'SAKA_SILO_REDIS_ENABLED\s*=\s*False', 'Désactivation redistribution hardcodée'),
    (r'#\s*TODO.*disable.*saka', 'TODO de désactivation SAKA'),
    (r'#\s*FIXME.*disable.*saka', 'FIXME de désactivation SAKA'),
]

# Extensions de fichiers binaires suspectes
BINARY_EXTENSIONS = ['.zip', '.exe', '.dll', '.so', '.dylib', '.bin', '.dat']


def is_excluded_file(file_path: str) -> bool:
    """Vérifie si un fichier doit être exclu"""
    for pattern in EXCLUDED_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def contains_secrets(file_path: Path) -> Tuple[bool, List[str]]:
    """Vérifie si un fichier contient des secrets"""
    if not file_path.exists() or not file_path.is_file():
        return False, []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False, []
    
    violations = []
    for pattern in SECRET_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Exclure les commentaires et docstrings
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:content.find('\n', match.start())]
            
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
            
            violations.append(f"Ligne {content[:match.start()].count('\n') + 1}: {match.group()[:50]}")
    
    return len(violations) > 0, violations


def contains_dangerous_code(file_path: Path) -> Tuple[bool, List[str]]:
    """Vérifie si un fichier contient du code dangereux"""
    if not file_path.exists() or not file_path.is_file():
        return False, []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False, []
    
    violations = []
    for pattern, description in DANGEROUS_CODE_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Exclure les commentaires et docstrings
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:content.find('\n', match.start())]
            
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
            
            # Vérifier si c'est dans un test (autorisé)
            if 'test' in str(file_path).lower() or 'override_settings' in content[:match.start()]:
                continue
            
            violations.append(f"{description} - Ligne {content[:match.start()].count('\n') + 1}")
    
    return len(violations) > 0, violations


def is_safe_file(file_path: str) -> Tuple[bool, str]:
    """Détermine si un fichier est sûr à commiter"""
    path = Path(file_path)
    
    # Exclure les fichiers système
    if is_excluded_file(file_path):
        return False, "Fichier système/temporaire exclu"
    
    # Vérifier les extensions binaires suspectes
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False, f"Fichier binaire suspect ({path.suffix})"
    
    # Vérifier les secrets
    has_secrets, secret_violations = contains_secrets(path)
    if has_secrets:
        return False, f"Secrets détectés: {', '.join(secret_violations[:2])}"
    
    # Vérifier le code dangereux
    has_dangerous, dangerous_violations = contains_dangerous_code(path)
    if has_dangerous:
        return False, f"Code dangereux: {', '.join(dangerous_violations[:2])}"
    
    return True, "OK"


def analyze_files(file_paths: List[str]) -> Dict[str, List[str]]:
    """Analyse une liste de fichiers et les classe"""
    safe_files = []
    rejected_files = []
    
    for file_path in file_paths:
        is_safe, reason = is_safe_file(file_path)
        if is_safe:
            safe_files.append(file_path)
        else:
            rejected_files.append((file_path, reason))
    
    return {
        'safe': safe_files,
        'rejected': rejected_files
    }


if __name__ == "__main__":
    # Récupérer les fichiers depuis stdin ou arguments
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Lire depuis stdin (git status --porcelain)
        files = [line.strip().split()[-1] for line in sys.stdin if line.strip()]
    
    result = analyze_files(files)
    
    # Afficher les résultats
    print("SAFE_FILES:")
    for f in result['safe']:
        print(f)
    
    print("\nREJECTED_FILES:")
    for f, reason in result['rejected']:
        print(f"{f}|{reason}")

