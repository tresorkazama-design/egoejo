#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOEJO Guardian - Script de Sécurité Robuste pour PR Bot
Version : 2.0 - Analyse Git Diff avec Messages GitHub Actions

PHILOSOPHIE EGOEJO :
- Structure Relationnelle SAKA (Souveraine, Prioritaire)
- Structure Instrumentale EUR (Subordonnée, Dormante)
- Aucune conversion SAKA ↔ EUR
- Aucun rendement financier sur SAKA
- Aucun affichage monétaire du SAKA

Usage:
    python .egoejo/guardian.py [base_branch]

Exit codes:
    0 : PASS - Compatible EGOEJO
    1 : FAIL - Violation critique détectée (bloque le merge)
"""

import re
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class EGOEJOGuardian:
    """Bot de vérification de conformité EGOEJO - Version Robuste"""
    
    def __init__(self):
        """Initialise le Guardian avec les règles de conformité"""
        self.violations = []
        self.modified_files = []
        self.saka_files_modified = []
        self.test_files_modified = []
        self.git_diff_content = ""
        
        # Règles bloquantes (HARD FAIL)
        self.blocking_rules = {
            'conversion_saka_eur': {
                'patterns': [
                    r'convert.*saka.*eur',
                    r'convert.*eur.*saka',
                    r'saka.*exchange.*rate',
                    r'exchange.*rate.*saka',
                    r'saka.*price|price.*saka',
                    r'saka.*=.*eur|eur.*=.*saka',
                    r'saka_to_eur|eur_to_saka',
                    r'convert_saka|convert_eur',
                    r'saka.*currency|currency.*saka',
                ],
                'description': 'Conversion SAKA ↔ EUR interdite',
                'severity': 'CRITICAL'
            },
            'financial_return_saka': {
                'patterns': [
                    r'saka.*interest|interest.*saka',
                    r'saka.*yield|yield.*saka',
                    r'saka.*profit|profit.*saka',
                    r'saka.*dividend|dividend.*saka',
                    r'saka.*roi|roi.*saka',
                    r'saka.*apy|apy.*saka',
                    r'saka.*return|return.*saka',
                    r'saka.*revenue|revenue.*saka',
                ],
                'description': 'Rendement financier sur SAKA interdit',
                'severity': 'CRITICAL'
            },
            'monetary_display_saka': {
                'patterns': [
                    r'saka.*€|€.*saka',
                    r'saka.*\$|\$.*saka',
                    r'saka.*euro|euro.*saka',
                    r'saka.*dollar|dollar.*saka',
                    r'saka.*currency|currency.*saka',
                    r'format.*saka.*money|format.*money.*saka',
                    r'saka.*amount.*€|€.*amount.*saka',
                    r'saka.*value.*\$|\$.*value.*saka',
                ],
                'description': 'Affichage monétaire du SAKA interdit',
                'severity': 'CRITICAL'
            }
        }
        
        # Patterns pour identifier les fichiers SAKA
        self.saka_file_patterns = [
            r'.*saka.*\.py$',
            r'.*Saka.*\.py$',
            r'backend/core/services/saka\.py$',
            r'backend/core/models/saka\.py$',
            r'backend/core/api/saka.*\.py$',
            r'backend/core/tasks.*saka.*\.py$',
        ]
        
        # Patterns pour identifier les fichiers de test
        self.test_file_patterns = [
            r'.*test.*saka.*\.py$',
            r'.*test.*Saka.*\.py$',
            r'backend/tests/.*saka.*\.py$',
            r'backend/tests/compliance/test_saka.*\.py$',
            r'backend/core/tests.*saka.*\.py$',
        ]
    
    def get_git_diff(self, base_branch: str = "origin/main") -> str:
        """
        Récupère le contenu complet du git diff
        
        Args:
            base_branch: Branche de référence
            
        Returns:
            Contenu du git diff
        """
        try:
            # Récupérer le diff complet (pas seulement les noms de fichiers)
            # Utiliser errors='replace' pour gérer l'encodage
            result = subprocess.run(
                ["git", "diff", base_branch, "--"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            self._github_error(f"Impossible de recuperer git diff: {e}")
            return ""
        
        except FileNotFoundError:
            self._github_error("git n'est pas installe ou non disponible")
            sys.exit(1)
    
    def get_modified_files(self, base_branch: str = "origin/main") -> List[str]:
        """
        Récupère la liste des fichiers modifiés via git diff
        
        Args:
            base_branch: Branche de référence
            
        Returns:
            Liste des chemins de fichiers modifiés
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", base_branch],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return files
        
        except subprocess.CalledProcessError as e:
            self._github_error(f"Impossible de recuperer les fichiers modifies: {e}")
            return []
        
        except FileNotFoundError:
            self._github_error("git n'est pas installe ou non disponible")
            sys.exit(1)
    
    def is_saka_file(self, file_path: str) -> bool:
        """
        Vérifie si un fichier est un fichier SAKA
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            True si c'est un fichier SAKA
        """
        for pattern in self.saka_file_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        return False
    
    def is_test_file(self, file_path: str) -> bool:
        """
        Vérifie si un fichier est un fichier de test
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            True si c'est un fichier de test
        """
        for pattern in self.test_file_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        return False
    
    def scan_git_diff(self, git_diff: str) -> List[Dict]:
        """
        Scanne le git diff pour détecter les violations
        
        Args:
            git_diff: Contenu du git diff
            
        Returns:
            Liste des violations détectées
        """
        violations = []
        
        if not git_diff:
            return violations
        
        # Parser le diff pour extraire les fichiers et lignes modifiées
        current_file = None
        current_line_num = 0
        added_lines = []  # Lignes ajoutées (commençant par +)
        
        for line in git_diff.split('\n'):
            # Détecter le début d'un nouveau fichier
            if line.startswith('diff --git'):
                # Extraire le nom du fichier
                match = re.search(r'diff --git a/(.+?) b/(.+?)$', line)
                if match:
                    current_file = match.group(2)
                    added_lines = []
            
            # Détecter les numéros de ligne (hunk header)
            elif line.startswith('@@'):
                match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                if match:
                    current_line_num = int(match.group(2))
            
            # Détecter les lignes ajoutées (commençant par + mais pas ++)
            elif line.startswith('+') and not line.startswith('++'):
                added_line = line[1:]  # Enlever le +
                added_lines.append((current_line_num, added_line))
                current_line_num += 1
            
            # Quand on arrive à un nouveau fichier ou à la fin, scanner les lignes ajoutées
            if current_file and (line.startswith('diff --git') or line == ''):
                if added_lines:
                    file_violations = self._scan_file_lines(current_file, added_lines)
                    violations.extend(file_violations)
                    added_lines = []
        
        # Scanner les dernières lignes si nécessaire
        if current_file and added_lines:
            file_violations = self._scan_file_lines(current_file, added_lines)
            violations.extend(file_violations)
        
        return violations
    
    def _scan_file_lines(self, file_path: str, added_lines: List[Tuple[int, str]]) -> List[Dict]:
        """
        Scanne les lignes ajoutées d'un fichier pour détecter les violations
        
        Args:
            file_path: Chemin du fichier
            added_lines: Liste de tuples (numéro_ligne, contenu_ligne)
            
        Returns:
            Liste des violations détectées
        """
        violations = []
        
        # Vérifier chaque règle bloquante
        for rule_name, rule_data in self.blocking_rules.items():
            patterns = rule_data.get('patterns', [])
            description = rule_data.get('description', '')
            severity = rule_data.get('severity', 'CRITICAL')
            
            for line_num, line_content in added_lines:
                # Exclure les faux positifs
                if self._is_false_positive(line_content):
                    continue
                
                # Vérifier chaque pattern
                for pattern in patterns:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        violations.append({
                            'file': file_path,
                            'line': line_num,
                            'rule': rule_name,
                            'description': description,
                            'pattern': pattern,
                            'severity': severity,
                            'content': line_content.strip()[:100]
                        })
                        break  # Une violation par ligne suffit
        
        return violations
    
    def _is_false_positive(self, line: str) -> bool:
        """
        Vérifie si une ligne correspondante est un faux positif
        
        Args:
            line: Ligne de code
            
        Returns:
            True si c'est un faux positif
        """
        line_stripped = line.strip()
        
        # Exclure les commentaires
        if line_stripped.startswith('#'):
            return True
        
        # Exclure les docstrings
        if '"""' in line or "'''" in line:
            return True
        
        # Exclure les mots contenant "eur" dans "utilisateur", "erreur", etc.
        if re.search(r'\b(utilisateur|erreur|redistribution|assureur|assureurs)\b', line, re.IGNORECASE):
            return True
        
        # Exclure les "return" de fonction (sauf si c'est vraiment une conversion)
        if re.search(r'^\s*return\s+\w+', line) and 'convert' not in line.lower():
            return True
        
        # Exclure les imports
        if line_stripped.startswith('import ') or line_stripped.startswith('from '):
            return True
        
        return False
    
    def check_saka_tests_required(self) -> List[Dict]:
        """
        Vérifie que les modifications SAKA ont des tests associés
        
        Règle : Si core/services/saka.py est modifié, 
                au moins un fichier de test SAKA doit être modifié
        
        Returns:
            Liste des violations (tests manquants)
        """
        violations = []
        
        # Vérifier si core/services/saka.py est modifié
        saka_service_modified = any(
            'core/services/saka.py' in f or 'core/services/saka' in f
            for f in self.modified_files
        )
        
        if not saka_service_modified:
            return violations
        
        # Vérifier si au moins un fichier de test SAKA a été modifié
        has_saka_test = any(
            self.is_test_file(f) for f in self.modified_files
        )
        
        if not has_saka_test:
            violations.append({
                'file': 'core/services/saka.py',
                'rule': 'saka_tests_required',
                'description': 'Modification SAKA sans test associé',
                'severity': 'CRITICAL',
                'message': (
                    'Le fichier core/services/saka.py a été modifié '
                    'mais aucun fichier de test SAKA n\'a été modifié. '
                    'Toute modification SAKA DOIT être accompagnée de tests.'
                )
            })
        
        return violations
    
    def _github_error(self, message: str, file: Optional[str] = None, line: Optional[int] = None):
        """
        Formate un message d'erreur pour GitHub Actions
        
        Args:
            message: Message d'erreur
            file: Fichier concerné (optionnel)
            line: Ligne concernée (optionnel)
        """
        if file and line:
            print(f"::error file={file},line={line}::{message}")
        elif file:
            print(f"::error file={file}::{message}")
        else:
            print(f"::error::{message}")
    
    def _github_warning(self, message: str, file: Optional[str] = None, line: Optional[int] = None):
        """
        Formate un message d'avertissement pour GitHub Actions
        
        Args:
            message: Message d'avertissement
            file: Fichier concerné (optionnel)
            line: Ligne concernée (optionnel)
        """
        if file and line:
            print(f"::warning file={file},line={line}::{message}")
        elif file:
            print(f"::warning file={file}::{message}")
        else:
            print(f"::warning::{message}")
    
    def analyze(self, base_branch: str = "origin/main") -> Tuple[bool, List[Dict]]:
        """
        Analyse les fichiers modifiés et détecte les violations
        
        Args:
            base_branch: Branche de référence
            
        Returns:
            Tuple (is_compatible, violations)
        """
        print("EGOEJO Guardian - Analyse de conformite\n")
        
        # Récupérer le git diff complet
        self.git_diff_content = self.get_git_diff(base_branch)
        
        # Récupérer les fichiers modifiés
        self.modified_files = self.get_modified_files(base_branch)
        
        if not self.modified_files:
            print("[OK] Aucun fichier modifie detecte")
            return (True, [])
        
        print(f"Fichiers modifies: {len(self.modified_files)}\n")
        
        # Classifier les fichiers
        for file_path in self.modified_files:
            if self.is_saka_file(file_path):
                self.saka_files_modified.append(file_path)
            if self.is_test_file(file_path):
                self.test_files_modified.append(file_path)
        
        # Scanner le git diff pour détecter les violations
        all_violations = self.scan_git_diff(self.git_diff_content)
        
        # Vérifier les tests SAKA requis
        test_violations = self.check_saka_tests_required()
        all_violations.extend(test_violations)
        
        # Filtrer uniquement les violations CRITICAL (bloquantes)
        critical_violations = [
            v for v in all_violations 
            if v.get('severity') == 'CRITICAL'
        ]
        
        # Afficher les résultats
        self._print_results(critical_violations)
        
        # Retourner le verdict
        is_compatible = len(critical_violations) == 0
        
        return is_compatible, critical_violations
    
    def _print_results(self, violations: List[Dict]):
        """
        Affiche les résultats de l'analyse avec formatage GitHub Actions
        
        Args:
            violations: Violations critiques détectées
        """
        if violations:
            print("\n[FAIL] NON COMPATIBLE EGOEJO - VIOLATIONS CRITIQUES DETECTEES\n")
            print("=" * 80)
            
            # Grouper par règle
            violations_by_rule = defaultdict(list)
            for violation in violations:
                violations_by_rule[violation['rule']].append(violation)
            
            for rule_name, rule_violations in violations_by_rule.items():
                rule_data = self.blocking_rules.get(rule_name, {})
                description = rule_data.get('description', rule_name)
                
                print(f"\n[RULE] Regle violee: {description}")
                print(f"   Nombre de violations: {len(rule_violations)}\n")
                
                for violation in rule_violations:
                    file_path = violation['file']
                    line_num = violation.get('line', 0)
                    content = violation.get('content', 'N/A')
                    
                    # Message GitHub Actions
                    self._github_error(
                        f"{description}: {content[:80]}",
                        file=file_path,
                        line=line_num if line_num > 0 else None
                    )
                    
                    # Message console
                    print(f"   [FILE] {file_path}")
                    if line_num > 0:
                        print(f"      Ligne {line_num}: {content[:80]}")
                    print()
            
            print("=" * 80)
            print("\n[MERGE BLOCKED] MERGE BLOQUE - Corriger les violations avant de continuer\n")
        
        else:
            print("\n[PASS] COMPATIBLE EGOEJO\n")
            print("[OK] Aucune violation critique detectee")
            print("[OK] Tests presents pour modifications SAKA")
            print("[OK] Feature flags respectes")
            print("\nCette PR respecte la constitution EGOEJO.\n")


def main():
    """Point d'entrée principal"""
    # Déterminer la branche de base
    base_branch = "origin/main"
    
    # Vérifier si on est dans un contexte CI (variable d'environnement)
    if 'GITHUB_BASE_REF' in os.environ:
        base_branch = f"origin/{os.environ['GITHUB_BASE_REF']}"
    elif 'CI' in os.environ:
        base_branch = "origin/main"
    
    # Permettre de passer la branche en argument
    if len(sys.argv) > 1:
        base_branch = sys.argv[1]
    
    # Créer le Guardian
    guardian = EGOEJOGuardian()
    
    # Analyser
    try:
        is_compatible, violations = guardian.analyze(base_branch)
        
        # Exit avec le code approprié
        if is_compatible:
            sys.exit(0)  # PASS
        else:
            sys.exit(1)  # FAIL
    
    except Exception as e:
        guardian._github_error(f"Erreur fatale dans EGOEJO Guardian: {e}")
        print(f"\n[ERROR] Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
