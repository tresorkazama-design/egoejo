#!/usr/bin/env python3
"""
Script d'audit de contenu EGOEJO - Police des Mots

Vérifie que le frontend et la documentation ne contiennent pas de mots interdits
et contiennent les mots requis (whitelist).

BLOCQUE le déploiement si violations détectées.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class Violation:
    """Violation détectée"""
    file: str
    line: int
    word: str
    context: str
    severity: str  # "error" ou "warning"


# LISTE NOIRE (Blacklist) - Mots Interdits
BLACKLIST_FINANCE = [
    "Investissement",
    "Rendement",
    "ROI",
    "Dividende",
    "Spéculation",
    "Crypto",
    "cryptocurrency",
    "cryptomonnaie",
    "trading",
    "profit",
    "gain financier",
]

BLACKLIST_SPIRITUEL = [
    "Vibration",
    "5D",
    "Ascension",
    "Canalisation",
    "énergie",
    "chakra",
    "aura",
]

BLACKLIST_ALL = BLACKLIST_FINANCE + BLACKLIST_SPIRITUEL

# LISTE BLANCHE (Whitelist) - Mots Requis
WHITELIST_REQUIRED = [
    "Subsistance",
    "Contribution",
    "Régénération",
    "SAKA",
    "compostage",
    "cycle",
]

# Extensions de fichiers à scanner
SCAN_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx',  # Frontend
    '.md', '.txt',  # Documentation
    '.py',  # Backend (pour vérification)
}

# Dossiers à exclure
EXCLUDE_DIRS = {
    'node_modules',
    '.git',
    'dist',
    'build',
    '.next',
    '__pycache__',
    '.pytest_cache',
    'venv',
    'env',
    'htmlcov',
}

# Fichiers/Dossiers de documentation de compliance à exclure (ils expliquent les règles)
EXCLUDE_COMPLIANCE_DOCS = {
    'docs/egoejo_compliance',
    'docs/compliance',
    'docs/legal',
    'docs/constitution',
    'docs/governance',
    'docs/institutionnel',
    'docs/reports',
    'docs/audit',
    'docs/philosophie',
    'docs/open-source',
    'docs/production',
    'docs/security',
    'docs/observability',
    'tests/compliance',  # Les tests de compliance contiennent les patterns interdits dans leurs messages
    'backend/tests/compliance',  # Tests de compliance backend
    'docs/governance',
    'docs/reports',
    'docs/institutionnel',
    'docs/open-source',
    'docs/production',
    'docs/security',
}


def should_scan_file(file_path: Path) -> bool:
    """Vérifie si un fichier doit être scanné"""
    # Vérifier l'extension
    if file_path.suffix not in SCAN_EXTENSIONS:
        return False
    
    # Vérifier les dossiers exclus
    parts = file_path.parts
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in parts:
            return False
    
    # Exclure les fichiers de documentation de compliance (ils expliquent les règles)
    file_str = str(file_path)
    for exclude_pattern in EXCLUDE_COMPLIANCE_DOCS:
        if exclude_pattern in file_str:
            return False
    
    return True


def scan_file_for_blacklist(file_path: Path) -> List[Violation]:
    """Scanne un fichier pour les mots interdits (blacklist)"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                line_lower = line.lower()
                
                # Vérifier chaque mot de la blacklist
                for word in BLACKLIST_ALL:
                    # Recherche insensible à la casse
                    pattern = re.compile(r'\b' + re.escape(word.lower()) + r'\b', re.IGNORECASE)
                    if pattern.search(line):
                        # Extraire le contexte (50 caractères avant/après)
                        match = pattern.search(line)
                        if match:
                            start = max(0, match.start() - 25)
                            end = min(len(line), match.end() + 25)
                            context = line[start:end].strip()
                            
                            violations.append(Violation(
                                file=str(file_path),
                                line=line_num,
                                word=word,
                                context=context,
                                severity="error"  # Toujours erreur pour blacklist
                            ))
    except Exception as e:
        print(f"⚠️ Erreur lors du scan de {file_path}: {e}", file=sys.stderr)
    
    return violations


def scan_file_for_whitelist(file_path: Path) -> Dict[str, bool]:
    """Scanne un fichier pour les mots requis (whitelist)"""
    found_words = {word: False for word in WHITELIST_REQUIRED}
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            
            for word in WHITELIST_REQUIRED:
                pattern = re.compile(r'\b' + re.escape(word.lower()) + r'\b', re.IGNORECASE)
                if pattern.search(content):
                    found_words[word] = True
    except Exception as e:
        print(f"⚠️ Erreur lors du scan de {file_path}: {e}", file=sys.stderr)
    
    return found_words


def scan_directory(root_dir: Path) -> Tuple[List[Violation], Dict[str, bool]]:
    """Scanne un répertoire récursivement"""
    all_violations = []
    whitelist_found = {word: False for word in WHITELIST_REQUIRED}
    
    # Scanner frontend
    frontend_dir = root_dir / 'frontend'
    if frontend_dir.exists():
        for file_path in frontend_dir.rglob('*'):
            if file_path.is_file() and should_scan_file(file_path):
                violations = scan_file_for_blacklist(file_path)
                all_violations.extend(violations)
                
                found = scan_file_for_whitelist(file_path)
                for word, found_status in found.items():
                    whitelist_found[word] = whitelist_found[word] or found_status
    
    # Scanner docs
    docs_dir = root_dir / 'docs'
    if docs_dir.exists():
        for file_path in docs_dir.rglob('*'):
            if file_path.is_file() and should_scan_file(file_path):
                violations = scan_file_for_blacklist(file_path)
                all_violations.extend(violations)
                
                found = scan_file_for_whitelist(file_path)
                for word, found_status in found.items():
                    whitelist_found[word] = whitelist_found[word] or found_status
    
    return all_violations, whitelist_found


def main():
    """Point d'entrée principal"""
    root_dir = Path(__file__).parent.parent
    
    print("🔍 Audit de contenu EGOEJO - Police des Mots")
    print("=" * 60)
    
    # Scanner le répertoire
    violations, whitelist_found = scan_directory(root_dir)
    
    # Afficher les violations (blacklist)
    if violations:
        print("\n❌ VIOLATIONS DÉTECTÉES (Blacklist):")
        print("=" * 60)
        for violation in violations:
            print(f"\n🚫 Fichier: {violation.file}")
            print(f"   Ligne {violation.line}: {violation.word}")
            print(f"   Contexte: ...{violation.context}...")
            print(f"   Sévérité: {violation.severity.upper()}")
    
    # Afficher les mots manquants (whitelist)
    missing_words = [word for word, found in whitelist_found.items() if not found]
    if missing_words:
        print("\n⚠️ MOTS REQUIS MANQUANTS (Whitelist):")
        print("=" * 60)
        for word in missing_words:
            print(f"   - {word}")
    
    # Déterminer le code de sortie
    exit_code = 0
    
    if violations:
        print(f"\n❌ {len(violations)} violation(s) détectée(s).")
        print("🚫 DÉPLOIEMENT BLOQUÉ.")
        exit_code = 1
    
    if missing_words:
        print(f"\n⚠️ {len(missing_words)} mot(s) requis manquant(s).")
        if not violations:  # Si pas de violations, warning seulement
            print("⚠️ DÉPLOIEMENT AUTORISÉ (avec avertissement).")
        else:
            exit_code = 1
    
    if not violations and not missing_words:
        print("\n✅ AUCUNE VIOLATION DÉTECTÉE.")
        print("✅ TOUS LES MOTS REQUIS PRÉSENTS.")
        print("✅ DÉPLOIEMENT AUTORISÉ.")
    
    print("\n" + "=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

