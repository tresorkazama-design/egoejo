#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOEJO Compliant Validator
Outil de validation pour vérifier la conformité d'un projet avec la Constitution EGOEJO

Usage:
    python tools/egoejo-validator.py [--project-path PATH] [--strict]

Exit codes:
    0 : COMPLIANT - Le projet respecte la Constitution EGOEJO
    1 : NON-COMPLIANT - Violations détectées
    2 : ERROR - Erreur de validation (fichier manquant, JSON invalide, etc.)
"""

import json
import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class EGOEJOValidator:
    """Validateur de conformité EGOEJO"""
    
    def __init__(self, project_path: str = ".", strict: bool = False):
        """
        Initialise le validateur
        
        Args:
            project_path: Chemin vers le projet à valider
            strict: Mode strict (échoue sur warnings)
        """
        self.project_path = Path(project_path).resolve()
        self.strict = strict
        self.violations = []
        self.warnings = []
        self.declaration = None
        
    def load_declaration(self) -> bool:
        """
        Charge le fichier egoejo.json
        
        Returns:
            True si chargé avec succès, False sinon
        """
        declaration_path = self.project_path / "egoejo.json"
        
        if not declaration_path.exists():
            self.violations.append({
                'type': 'error',
                'message': f'Fichier egoejo.json introuvable dans {self.project_path}',
                'file': 'egoejo.json'
            })
            return False
        
        try:
            with open(declaration_path, 'r', encoding='utf-8') as f:
                self.declaration = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.violations.append({
                'type': 'error',
                'message': f'Erreur de parsing JSON: {e}',
                'file': 'egoejo.json'
            })
            return False
        except Exception as e:
            self.violations.append({
                'type': 'error',
                'message': f'Erreur lors du chargement: {e}',
                'file': 'egoejo.json'
            })
            return False
    
    def validate_schema(self) -> bool:
        """
        Valide la structure du JSON selon le schéma
        
        Returns:
            True si valide, False sinon
        """
        if not self.declaration:
            return False
        
        required_fields = [
            'version', 'project_name', 'project_url',
            'constitution_version', 'saka_structure', 'separation_rules'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in self.declaration:
                missing_fields.append(field)
        
        if missing_fields:
            self.violations.append({
                'type': 'error',
                'message': f'Champs requis manquants: {", ".join(missing_fields)}',
                'file': 'egoejo.json'
            })
            return False
        
        return True
    
    def validate_saka_structure(self) -> bool:
        """
        Valide la déclaration de la structure SAKA
        
        Returns:
            True si valide, False sinon
        """
        if not self.declaration or 'saka_structure' not in self.declaration:
            return False
        
        saka = self.declaration['saka_structure']
        valid = True
        
        # Vérifier que SAKA est activé si compost est activé
        if saka.get('compost_enabled', False) and not saka.get('enabled', False):
            self.violations.append({
                'type': 'violation',
                'message': 'Le compostage ne peut pas être activé si SAKA est désactivé',
                'file': 'egoejo.json',
                'rule': 'saka_structure_consistency'
            })
            valid = False
        
        # Vérifier que le compostage est activé (règle fondamentale)
        if saka.get('enabled', False) and not saka.get('compost_enabled', False):
            self.violations.append({
                'type': 'violation',
                'message': 'Le compostage DOIT être activé si SAKA est activé (règle fondamentale)',
                'file': 'egoejo.json',
                'rule': 'compost_mandatory'
            })
            valid = False
        
        # Vérifier les valeurs des paramètres
        if saka.get('compost_rate', 0) <= 0:
            self.warnings.append({
                'type': 'warning',
                'message': 'Le taux de compostage est à 0 ou négatif',
                'file': 'egoejo.json'
            })
        
        if saka.get('compost_inactivity_days', 0) <= 0:
            self.violations.append({
                'type': 'violation',
                'message': 'Le nombre de jours d\'inactivité doit être > 0',
                'file': 'egoejo.json',
                'rule': 'compost_inactivity_days'
            })
            valid = False
        
        return valid
    
    def validate_separation_rules(self) -> bool:
        """
        Valide les règles de séparation
        
        Returns:
            True si valide, False sinon
        """
        if not self.declaration or 'separation_rules' not in self.declaration:
            return False
        
        rules = self.declaration['separation_rules']
        valid = True
        
        # Vérifier que toutes les règles fondamentales sont à True
        fundamental_rules = [
            'strict_separation',
            'no_conversion',
            'no_financial_return',
            'no_monetary_display'
        ]
        
        for rule in fundamental_rules:
            if not rules.get(rule, False):
                self.violations.append({
                    'type': 'violation',
                    'message': f'La règle "{rule}" DOIT être à True (règle fondamentale)',
                    'file': 'egoejo.json',
                    'rule': rule
                })
                valid = False
        
        return valid
    
    def validate_code_separation(self) -> bool:
        """
        Valide la séparation dans le code source
        
        Returns:
            True si valide, False sinon
        """
        if not self.declaration or 'code_locations' not in self.declaration:
            return True  # Optionnel
        
        code_locations = self.declaration.get('code_locations', {})
        valid = True
        
        saka_files = []
        monetary_files = []
        
        # Collecter les fichiers SAKA
        for pattern in code_locations.get('saka_models', []) + \
                      code_locations.get('saka_services', []):
            file_path = self.project_path / pattern
            if file_path.exists():
                saka_files.append(file_path)
        
        # Collecter les fichiers monétaires
        for pattern in code_locations.get('monetary_models', []):
            file_path = self.project_path / pattern
            if file_path.exists():
                monetary_files.append(file_path)
        
        # Vérifier qu'aucun fichier SAKA ne contient de références monétaires
        for saka_file in saka_files:
            violations = self._check_file_separation(saka_file, 'saka')
            if violations:
                self.violations.extend(violations)
                valid = False
        
        # Vérifier qu'aucun fichier monétaire ne contient de références SAKA
        for monetary_file in monetary_files:
            violations = self._check_file_separation(monetary_file, 'monetary')
            if violations:
                self.violations.extend(violations)
                valid = False
        
        return valid
    
    def _check_file_separation(self, file_path: Path, file_type: str) -> List[Dict]:
        """
        Vérifie la séparation dans un fichier
        
        Args:
            file_path: Chemin du fichier
            file_type: Type de fichier ('saka' ou 'monetary')
        
        Returns:
            Liste des violations détectées
        """
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return violations  # Ignorer les erreurs de lecture
        
        # Patterns interdits selon le type de fichier
        if file_type == 'saka':
            forbidden_patterns = [
                (r'\bUserWallet\b|\buser_wallet\b|\bEUR\b(?!\w)|\beuro\b(?!\w)|\$|€', 'Référence monétaire dans fichier SAKA'),
                (r'convert.*saka.*eur|convert.*eur.*saka', 'Conversion SAKA/EUR'),
                (r'saka.*interest|saka.*yield|saka.*roi', 'Rendement financier sur SAKA'),
            ]
        else:  # monetary
            forbidden_patterns = [
                (r'SakaWallet|saka_wallet|SAKA', 'Référence SAKA dans fichier monétaire'),
                (r'convert.*saka.*eur|convert.*eur.*saka', 'Conversion SAKA/EUR'),
            ]
        
        for pattern, description in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Exclure les commentaires et docstrings
                line_start = content.rfind('\n', 0, match.start()) + 1
                line = content[line_start:content.find('\n', match.start())]
                
                # Exclure les commentaires
                if line.strip().startswith('#'):
                    continue
                
                # Exclure les docstrings (détecter si on est dans une docstring)
                # Vérifier si la ligne est dans une docstring
                docstring_start = content.rfind('"""', 0, match.start())
                docstring_end = content.find('"""', match.start())
                if docstring_start != -1 and (docstring_end == -1 or docstring_end > match.start()):
                    continue  # Dans une docstring
                
                # Exclure les commentaires multi-lignes
                if '"""' in line or "'''" in line:
                    continue
                
                # Exclure les lignes qui expliquent la séparation (philosophie)
                if re.search(r'(séparée|separated|séparation|separation).*(euro|eur|yang)', line, re.IGNORECASE):
                    continue
                
                # Exclure les mots contenant "eur" dans "utilisateur", "erreur", etc.
                if re.search(r'\b(utilisateur|erreur|redistribution|assureur|assureurs|structure.*relationnelle|structure.*instrumentale)\b', line, re.IGNORECASE):
                    continue
                
                # Exclure les imports
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    continue
                
                line_num = content[:match.start()].count('\n') + 1
                violations.append({
                    'type': 'violation',
                    'message': f'{description}: {match.group()}',
                    'file': str(file_path.relative_to(self.project_path)),
                    'line': line_num,
                    'rule': 'code_separation'
                })
        
        return violations
    
    def validate_tests(self) -> bool:
        """
        Valide la présence de tests de conformité
        
        Returns:
            True si valide, False sinon
        """
        if not self.declaration or 'code_locations' not in self.declaration:
            return True  # Optionnel
        
        code_locations = self.declaration.get('code_locations', {})
        test_files = code_locations.get('saka_tests', [])
        
        if not test_files:
            self.warnings.append({
                'type': 'warning',
                'message': 'Aucun fichier de test SAKA déclaré',
                'file': 'egoejo.json'
            })
            return True  # Warning seulement
        
        # Vérifier que les fichiers de test existent
        missing_tests = []
        for pattern in test_files:
            file_path = self.project_path / pattern
            if not file_path.exists():
                missing_tests.append(pattern)
        
        if missing_tests:
            self.warnings.append({
                'type': 'warning',
                'message': f'Fichiers de test déclarés mais introuvables: {", ".join(missing_tests)}',
                'file': 'egoejo.json'
            })
        
        return True
    
    def validate(self) -> Tuple[bool, List[Dict], List[Dict]]:
        """
        Exécute toutes les validations
        
        Returns:
            Tuple (is_compliant, violations, warnings)
        """
        # Charger la déclaration
        if not self.load_declaration():
            return (False, self.violations, self.warnings)
        
        # Valider le schéma
        if not self.validate_schema():
            return (False, self.violations, self.warnings)
        
        # Valider la structure SAKA
        self.validate_saka_structure()
        
        # Valider les règles de séparation
        self.validate_separation_rules()
        
        # Valider la séparation dans le code
        self.validate_code_separation()
        
        # Valider les tests
        self.validate_tests()
        
        # Déterminer si conforme
        is_compliant = len([v for v in self.violations if v['type'] == 'violation']) == 0
        
        # En mode strict, les warnings sont des violations
        if self.strict and self.warnings:
            self.violations.extend(self.warnings)
            is_compliant = False
        
        return (is_compliant, self.violations, self.warnings)
    
    def print_report(self, is_compliant: bool, violations: List[Dict], warnings: List[Dict]):
        """
        Affiche le rapport de validation
        
        Args:
            is_compliant: True si conforme
            violations: Liste des violations
            warnings: Liste des avertissements
        """
        print("=" * 80)
        print("EGOEJO Compliant Validator - Rapport de Validation")
        print("=" * 80)
        print()
        
        if is_compliant:
            print("[PASS] PROJET CONFORME A LA CONSTITUTION EGOEJO")
            print()
        else:
            print("[FAIL] PROJET NON CONFORME - VIOLATIONS DETECTEES")
            print()
        
        # Afficher les violations
        if violations:
            print(f"[VIOLATIONS] Violations ({len(violations)}):")
            print()
            for violation in violations:
                print(f"  [{violation['type'].upper()}] {violation['message']}")
                if 'file' in violation:
                    print(f"      Fichier: {violation['file']}")
                if 'line' in violation:
                    print(f"      Ligne: {violation['line']}")
                if 'rule' in violation:
                    print(f"      Regle: {violation['rule']}")
                print()
        
        # Afficher les avertissements
        if warnings:
            print(f"[WARNINGS] Avertissements ({len(warnings)}):")
            print()
            for warning in warnings:
                print(f"  [{warning['type'].upper()}] {warning['message']}")
                if 'file' in warning:
                    print(f"      Fichier: {warning['file']}")
                print()
        
        print("=" * 80)


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Validateur de conformité EGOEJO Compliant'
    )
    parser.add_argument(
        '--project-path',
        type=str,
        default='.',
        help='Chemin vers le projet à valider (défaut: répertoire courant)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Mode strict (les warnings sont traités comme des violations)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Sortie au format JSON'
    )
    
    args = parser.parse_args()
    
    # Créer le validateur
    validator = EGOEJOValidator(
        project_path=args.project_path,
        strict=args.strict
    )
    
    # Exécuter la validation
    is_compliant, violations, warnings = validator.validate()
    
    # Afficher le rapport
    if args.json:
        report = {
            'compliant': is_compliant,
            'violations': violations,
            'warnings': warnings,
            'violation_count': len(violations),
            'warning_count': len(warnings)
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        validator.print_report(is_compliant, violations, warnings)
    
    # Exit code
    if is_compliant:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

