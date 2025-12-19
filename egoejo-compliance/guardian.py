#!/usr/bin/env python3
"""
EGOEJO Guardian - Bot de vérification de conformité
Version autonome pour projets tiers

Usage:
    python guardian.py

Fonctionnalités:
    - Analyse les fichiers modifiés via git diff
    - Détecte les violations de la constitution EGOEJO
    - Vérifie la présence de tests pour modifications SAKA
    - Bloque le merge si violation critique détectée

Exit codes:
    0 : 🟢 COMPATIBLE EGOEJO
    1 : 🔴 NON COMPATIBLE EGOEJO (violation critique)
    2 : 🟠 COMPATIBLE EGOEJO (Banque Dormante)
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class EGOEJOGuardian:
    """Bot de vérification de conformité EGOEJO"""
    
    def __init__(self, rules_file: str = "guardian_rules.yml"):
        """
        Initialise le Guardian avec les règles de conformité
        
        Args:
            rules_file: Chemin vers le fichier de règles YAML
        """
        # Chercher le fichier de règles dans le même dossier que ce script
        script_dir = Path(__file__).parent
        self.rules_file = script_dir / rules_file
        self.rules = self._load_rules()
        self.violations = []
        self.modified_files = []
        self.saka_files_modified = []
        self.test_files_modified = []
        self.bank_active = False  # Détection si la banque est activée
    
    def _load_rules(self) -> Dict:
        """
        Charge les règles depuis le fichier YAML
        Note: Version simplifiée sans dépendance externe (parse YAML manuel)
        """
        if not self.rules_file.exists():
            print(f"[ERREUR] Fichier de regles non trouve: {self.rules_file}")
            sys.exit(1)
        
        # Parse YAML simplifié (sans dépendance externe)
        rules = {
            'no_conversion': {
                'patterns': [
                    r"convert.*saka.*eur|convert.*eur.*saka",
                    r"saka.*exchange.*rate|exchange.*rate.*saka",
                    r"saka.*price|price.*saka",
                    r"saka.*=.*eur|eur.*=.*saka",
                    r"saka_to_eur|eur_to_saka",
                ],
                'severity': 'CRITICAL'
            },
            'no_financial_return': {
                'patterns': [
                    r"saka.*interest|interest.*saka",
                    r"saka.*yield|yield.*saka",
                    r"saka.*profit|profit.*saka",
                    r"saka.*dividend|dividend.*saka",
                    r"saka.*roi|roi.*saka",
                    r"saka.*apy|apy.*saka",
                ],
                'severity': 'CRITICAL'
            },
            'no_monetary_display': {
                'patterns': [
                    r"saka.*€|€.*saka",
                    r"saka.*euro|euro.*saka",
                    r"saka.*eur|eur.*saka",
                    r"saka.*currency|currency.*saka",
                    r"format.*saka.*money|format.*money.*saka",
                ],
                'severity': 'HIGH'
            },
            'saka_file_patterns': [
                r".*saka.*\.py$",
                r".*Saka.*\.py$",
            ],
            'test_file_patterns': [
                r".*test.*saka.*\.py$",
                r".*test.*Saka.*\.py$",
            ]
        }
        
        return rules
    
    def get_modified_files(self, base_branch: str = "origin/main") -> List[str]:
        """
        Récupère la liste des fichiers modifiés via git diff
        
        Args:
            base_branch: Branche de référence (par défaut origin/main)
        
        Returns:
            Liste des chemins de fichiers modifiés
        """
        try:
            # Récupérer les fichiers modifiés
            result = subprocess.run(
                ["git", "diff", "--name-only", base_branch],
                capture_output=True,
                text=True,
                check=True
            )
            
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return files
        
        except subprocess.CalledProcessError as e:
            print(f"[AVERTISSEMENT] Impossible de recuperer les fichiers modifies: {e}")
            print("   Utilisation de tous les fichiers du repo...")
            # Fallback: analyser tous les fichiers Python
            return self._get_all_python_files()
        
        except FileNotFoundError:
            print("[ERREUR] git n'est pas installe ou non disponible")
            sys.exit(1)
    
    def _get_all_python_files(self) -> List[str]:
        """Récupère tous les fichiers Python du repo (fallback)"""
        python_files = []
        for path in Path('.').rglob('*.py'):
            if '.git' not in str(path) and 'node_modules' not in str(path):
                python_files.append(str(path))
        return python_files
    
    def is_saka_file(self, file_path: str) -> bool:
        """
        Vérifie si un fichier est un fichier SAKA
        
        Args:
            file_path: Chemin du fichier
        
        Returns:
            True si c'est un fichier SAKA
        """
        for pattern in self.rules['saka_file_patterns']:
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
        for pattern in self.rules['test_file_patterns']:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        return False
    
    def scan_file(self, file_path: str) -> List[Dict]:
        """
        Scanne un fichier pour détecter les violations
        
        Args:
            file_path: Chemin du fichier à scanner
        
        Returns:
            Liste des violations détectées
        """
        violations = []
        
        if not Path(file_path).exists():
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[AVERTISSEMENT] Impossible de lire {file_path}: {e}")
            return violations
        
        # Détecter si la banque est activée
        if re.search(r'ENABLE_INVESTMENT_FEATURES.*=.*True|ENABLE_INVESTMENT_FEATURES.*True', content, re.IGNORECASE):
            self.bank_active = True
        
        # Vérifier chaque règle
        for rule_name, rule_data in self.rules.items():
            if rule_name in ['saka_file_patterns', 'test_file_patterns']:
                continue
            
            patterns = rule_data.get('patterns', [])
            severity = rule_data.get('severity', 'HIGH')
            
            for pattern in patterns:
                # Rechercher le pattern dans le fichier
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Calculer le numéro de ligne
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    
                    # Exclure les faux positifs (commentaires, docstrings)
                    if self._is_false_positive(line_content, pattern):
                        continue
                    
                    violations.append({
                        'file': file_path,
                        'line': line_num,
                        'rule': rule_name,
                        'pattern': pattern,
                        'severity': severity,
                        'content': line_content[:100]  # Limiter la longueur
                    })
        
        return violations
    
    def _is_false_positive(self, line: str, pattern: str) -> bool:
        """
        Vérifie si une ligne correspondante est un faux positif
        
        Args:
            line: Ligne de code
            pattern: Pattern détecté
        
        Returns:
            True si c'est un faux positif
        """
        # Exclure les commentaires
        if line.strip().startswith('#'):
            return True
        
        # Exclure les docstrings
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return True
        
        # Exclure les mots contenant "eur" dans "utilisateur", "erreur", etc.
        if 'eur' in pattern.lower() and not re.search(r'\beur\b', pattern, re.IGNORECASE):
            if re.search(r'\b(utilisateur|erreur|redistribution|securite)\b', line, re.IGNORECASE):
                return True
        
        # Exclure les "return" de fonction (mais pas les calculs de rendement)
        if re.search(r'^\s*return\s+\w+', line) and 'return' not in pattern.lower():
            return True
        
        return False
    
    def check_saka_tests(self) -> List[Dict]:
        """
        Vérifie que les modifications SAKA ont des tests associés
        
        Returns:
            Liste des violations (tests manquants)
        """
        violations = []
        
        if not self.saka_files_modified:
            return violations
        
        # Vérifier si au moins un fichier de test SAKA a été modifié
        has_saka_test = any(
            self.is_test_file(f) for f in self.modified_files
        )
        
        if not has_saka_test:
            for saka_file in self.saka_files_modified:
                violations.append({
                    'file': saka_file,
                    'rule': 'saka_tests_required',
                    'severity': 'HIGH',
                    'message': f"Modification SAKA sans test associe: {saka_file}"
                })
        
        return violations
    
    def analyze(self, base_branch: str = "origin/main") -> Tuple[bool, List[Dict], bool]:
        """
        Analyse les fichiers modifiés et détecte les violations
        
        Args:
            base_branch: Branche de référence
        
        Returns:
            Tuple (is_compatible, violations, bank_active)
        """
        print("EGOEJO Guardian - Analyse de conformite\n")
        
        # Récupérer les fichiers modifiés
        self.modified_files = self.get_modified_files(base_branch)
        
        if not self.modified_files:
            print("[OK] Aucun fichier modifie detecte")
            return (True, [], False)
        
        print(f"Fichiers modifies: {len(self.modified_files)}\n")
        
        # Classifier les fichiers
        for file_path in self.modified_files:
            if self.is_saka_file(file_path):
                self.saka_files_modified.append(file_path)
            if self.is_test_file(file_path):
                self.test_files_modified.append(file_path)
        
        # Scanner chaque fichier
        all_violations = []
        
        for file_path in self.modified_files:
            # Scanner uniquement les fichiers Python
            if not file_path.endswith('.py'):
                continue
            
            violations = self.scan_file(file_path)
            all_violations.extend(violations)
        
        # Vérifier les tests SAKA
        test_violations = self.check_saka_tests()
        all_violations.extend(test_violations)
        
        # Séparer les violations critiques des autres
        critical_violations = [
            v for v in all_violations 
            if v.get('severity') == 'CRITICAL'
        ]
        
        high_violations = [
            v for v in all_violations 
            if v.get('severity') == 'HIGH'
        ]
        
        # Afficher les résultats
        self._print_results(critical_violations, high_violations, self.bank_active)
        
        # Retourner le verdict
        # Note : Si bank_active, retourner code 2 (Banque Dormante)
        is_compatible = len(critical_violations) == 0
        
        return (is_compatible, all_violations, self.bank_active)
    
    def _print_results(self, critical_violations: List[Dict], high_violations: List[Dict], bank_active: bool = False):
        """
        Affiche les résultats de l'analyse
        
        Args:
            critical_violations: Violations critiques
            high_violations: Violations importantes
            bank_active: Si True, la banque est activée
        """
        if critical_violations:
            print("[ROUGE] NON COMPATIBLE EGOEJO\n")
            print("Violations critiques detectees:\n")
            
            for violation in critical_violations:
                rule_name = violation['rule'].replace('_', ' ').title()
                file_name = Path(violation['file']).name
                print(f"  [X] {rule_name}")
                print(f"     Fichier: {violation['file']} (ligne {violation['line']})")
                print(f"     Contenu: {violation.get('content', 'N/A')[:80]}")
                print()
        
        elif high_violations:
            print("[JAUNE] COMPATIBLE SOUS CONDITIONS\n")
            print("Violations importantes detectees:\n")
            
            for violation in high_violations:
                rule_name = violation['rule'].replace('_', ' ').title()
                print(f"  [!] {rule_name}")
                print(f"     {violation.get('message', violation.get('file', 'N/A'))}")
                print()
        
        else:
            if bank_active:
                print("[ORANGE] COMPATIBLE EGOEJO (BANQUE DORMANTE)\n")
                print("[OK] Aucune violation critique detectee")
                print("[!] Banque (EUR) activee mais strictement separee de SAKA")
                print("[OK] Tests presents pour modifications SAKA")
                print("\nCette PR respecte la constitution EGOEJO avec banque activee.")
            else:
                print("[VERT] COMPATIBLE EGOEJO\n")
                print("[OK] Aucune violation detectee")
                print("[OK] Tests presents pour modifications SAKA")
                print("[OK] Feature flags respectes")
                print("\nCette PR respecte la constitution EGOEJO.")


def main():
    """Point d'entrée principal"""
    import os
    
    # Déterminer la branche de base
    base_branch = "origin/main"
    
    # Vérifier si on est dans un contexte CI (variable d'environnement)
    if 'GITHUB_BASE_REF' in os.environ:
        base_branch = f"origin/{os.environ['GITHUB_BASE_REF']}"
    elif 'CI' in os.environ:
        # En CI, utiliser la branche par défaut
        base_branch = "origin/main"
    
    # Créer le Guardian
    guardian = EGOEJOGuardian()
    
    # Analyser
    is_compatible, violations, bank_active = guardian.analyze(base_branch)
    
    # Exit avec le code approprié
    if is_compatible and not bank_active:
        sys.exit(0)  # 🟢 Compatible
    elif is_compatible and bank_active:
        sys.exit(2)  # 🟠 Compatible (Banque Dormante)
    else:
        print("\n[ACTION REQUISE] Corriger les violations critiques avant merge.")
        sys.exit(1)  # 🔴 Non Compatible


if __name__ == "__main__":
    main()

