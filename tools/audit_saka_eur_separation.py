#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit de Séparation SAKA/EUR - Production Excellence
Détecte toute jointure ou fusion entre SakaWallet et UserWallet
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Ajouter le répertoire backend au path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import connection
from django.apps import apps


class SakaEurSeparationAuditor:
    """Auditeur de séparation SAKA/EUR"""
    
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.checks_passed = []
    
    def audit_sql_queries(self) -> List[Dict]:
        """
        Audite toutes les requêtes SQL pour détecter les jointures SAKA/EUR.
        """
        violations = []
        
        # Patterns interdits dans les requêtes SQL
        forbidden_patterns = [
            # Jointures explicites
            r'JOIN.*saka.*wallet.*JOIN.*user.*wallet',
            r'JOIN.*user.*wallet.*JOIN.*saka.*wallet',
            r'FROM.*saka.*wallet.*JOIN.*user.*wallet',
            r'FROM.*user.*wallet.*JOIN.*saka.*wallet',
            
            # Jointures Django ORM (détection dans le code)
            r'SakaWallet.*objects.*filter.*user.*wallet',
            r'UserWallet.*objects.*filter.*saka.*wallet',
            r'\.saka_wallet.*\.wallet',
            r'\.wallet.*\.saka_wallet',
            
            # Fusion de données
            r'merge.*saka.*eur|merge.*eur.*saka',
            r'combine.*saka.*eur|combine.*eur.*saka',
            r'union.*saka.*eur|union.*eur.*saka',
        ]
        
        # Scanner les fichiers Python
        backend_path = Path(__file__).parent.parent / "backend"
        
        for py_file in backend_path.rglob("*.py"):
            # Ignorer les migrations et les tests (sauf tests compliance)
            if "migrations" in str(py_file) and "0027" not in str(py_file):
                continue
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append({
                            'file': str(py_file.relative_to(backend_path.parent)),
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group(0),
                            'severity': 'CRITICAL'
                        })
            except Exception as e:
                self.warnings.append(f"Erreur lecture {py_file}: {e}")
        
        return violations
    
    def audit_serializers(self) -> List[Dict]:
        """
        Audite les serializers pour détecter la fusion SAKA/EUR.
        """
        violations = []
        
        serializer_path = backend_path / "core" / "serializers"
        
        if not serializer_path.exists():
            return violations
        
        for serializer_file in serializer_path.glob("*.py"):
            try:
                content = serializer_file.read_text(encoding='utf-8')
                
                # Patterns interdits dans les serializers
                forbidden_patterns = [
                    r'saka.*wallet.*user.*wallet|user.*wallet.*saka.*wallet',
                    r'balance.*saka.*eur|balance.*eur.*saka',
                    r'fields.*=.*\[.*saka.*wallet.*user.*wallet',
                ]
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append({
                            'file': str(serializer_file.relative_to(backend_path.parent)),
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group(0),
                            'severity': 'CRITICAL'
                        })
            except Exception as e:
                self.warnings.append(f"Erreur lecture {serializer_file}: {e}")
        
        return violations
    
    def audit_api_views(self) -> List[Dict]:
        """
        Audite les vues API pour détecter la fusion SAKA/EUR.
        """
        violations = []
        
        api_path = backend_path / "core" / "api"
        
        if not api_path.exists():
            return violations
        
        for view_file in api_path.glob("*.py"):
            try:
                content = view_file.read_text(encoding='utf-8')
                
                # Patterns interdits dans les vues API
                forbidden_patterns = [
                    r'saka.*wallet.*user.*wallet|user.*wallet.*saka.*wallet',
                    r'\.saka_wallet.*\.wallet|\.wallet.*\.saka_wallet',
                    r'balance.*saka.*balance.*eur',
                ]
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append({
                            'file': str(view_file.relative_to(backend_path.parent)),
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group(0),
                            'severity': 'CRITICAL'
                        })
            except Exception as e:
                self.warnings.append(f"Erreur lecture {view_file}: {e}")
        
        return violations
    
    def check_database_constraints(self) -> Tuple[bool, str]:
        """
        Vérifie que la contrainte de séparation SAKA/EUR est présente en DB.
        """
        if connection.vendor != 'postgresql':
            return (True, "SQLite détecté : Contrainte DB non applicable (OK pour dev)")
        
        try:
            with connection.cursor() as cursor:
                # Vérifier si la vue existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.views 
                        WHERE table_name = 'saka_eur_separation_check'
                    );
                """)
                view_exists = cursor.fetchone()[0]
                
                if not view_exists:
                    return (False, "Vue saka_eur_separation_check absente")
                
                # Vérifier si la fonction existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_proc 
                        WHERE proname = 'check_saka_eur_separation'
                    );
                """)
                function_exists = cursor.fetchone()[0]
                
                if not function_exists:
                    return (False, "Fonction check_saka_eur_separation absente")
                
                return (True, "Contrainte DB présente")
        except Exception as e:
            return (False, f"Erreur vérification DB : {e}")
    
    def run_audit(self) -> Dict:
        """
        Exécute l'audit complet.
        """
        print("🔍 Audit de Séparation SAKA/EUR - Production Excellence\n")
        print("=" * 80)
        
        # 1. Audit SQL Queries
        print("\n[1/4] Audit des requêtes SQL...")
        sql_violations = self.audit_sql_queries()
        if sql_violations:
            self.violations.extend(sql_violations)
            print(f"❌ {len(sql_violations)} violation(s) détectée(s)")
        else:
            print("✅ Aucune violation détectée")
            self.checks_passed.append("SQL Queries")
        
        # 2. Audit Serializers
        print("\n[2/4] Audit des serializers...")
        serializer_violations = self.audit_serializers()
        if serializer_violations:
            self.violations.extend(serializer_violations)
            print(f"❌ {len(serializer_violations)} violation(s) détectée(s)")
        else:
            print("✅ Aucune violation détectée")
            self.checks_passed.append("Serializers")
        
        # 3. Audit API Views
        print("\n[3/4] Audit des vues API...")
        view_violations = self.audit_api_views()
        if view_violations:
            self.violations.extend(view_violations)
            print(f"❌ {len(view_violations)} violation(s) détectée(s)")
        else:
            print("✅ Aucune violation détectée")
            self.checks_passed.append("API Views")
        
        # 4. Vérification Contrainte DB
        print("\n[4/4] Vérification contrainte base de données...")
        db_ok, db_message = self.check_database_constraints()
        if db_ok:
            print(f"✅ {db_message}")
            self.checks_passed.append("Database Constraints")
        else:
            print(f"⚠️  {db_message}")
            self.warnings.append(db_message)
        
        # Résumé
        print("\n" + "=" * 80)
        print("\n📊 RÉSUMÉ DE L'AUDIT\n")
        
        print(f"✅ Checks passés : {len(self.checks_passed)}")
        for check in self.checks_passed:
            print(f"   - {check}")
        
        if self.violations:
            print(f"\n❌ Violations détectées : {len(self.violations)}")
            for violation in self.violations:
                print(f"   - {violation['file']}:{violation['line']} - {violation['match'][:50]}")
        
        if self.warnings:
            print(f"\n⚠️  Avertissements : {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        # Verdict
        is_compliant = len(self.violations) == 0
        
        print("\n" + "=" * 80)
        if is_compliant:
            print("\n✅ CONFORME : Séparation SAKA/EUR respectée")
            return {
                'compliant': True,
                'violations': [],
                'warnings': self.warnings,
                'checks_passed': self.checks_passed
            }
        else:
            print("\n❌ NON CONFORME : Violations de séparation SAKA/EUR détectées")
            return {
                'compliant': False,
                'violations': self.violations,
                'warnings': self.warnings,
                'checks_passed': self.checks_passed
            }


def main():
    """Point d'entrée principal"""
    auditor = SakaEurSeparationAuditor()
    result = auditor.run_audit()
    
    # Exit code
    sys.exit(0 if result['compliant'] else 1)


if __name__ == "__main__":
    main()

