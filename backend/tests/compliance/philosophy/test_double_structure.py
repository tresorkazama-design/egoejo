"""
EGOEJO Compliance Test : Double Structure (Relationnelle > Instrumentale)

LOI EGOEJO :
"La structure relationnelle (SAKA) prime toujours sur la structure instrumentale (EUR)."

Ce test vérifie que :
- Aucune fonction ne permet de convertir SAKA en EUR
- SAKA n'est jamais affiché comme monnaie
- La structure relationnelle est toujours prioritaire

Violation du Manifeste EGOEJO si :
- Une fonction convert_saka_to_eur() existe
- SAKA est affiché avec un symbole monétaire (€, $, etc.)
- La structure instrumentale prime sur la relationnelle
"""
import pytest
import re
from pathlib import Path


@pytest.mark.egoejo_compliance
class TestDoubleStructure:
    """
    Tests de conformité : Double Structure (Relationnelle > Instrumentale)
    
    RÈGLE ABSOLUE : La structure relationnelle (SAKA) prime toujours sur la structure instrumentale (EUR).
    """
    
    def test_aucune_conversion_saka_vers_eur(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une fonction permet de convertir SAKA en EUR.
        
        Test : Scanner le code pour détecter les fonctions de conversion.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        
        # Patterns interdits pour conversion SAKA → EUR
        forbidden_patterns = [
            r"def\s+convert.*saka.*eur",
            r"def\s+convert.*eur.*saka",
            r"def\s+saka.*to.*eur",
            r"def\s+eur.*to.*saka",
            r"saka.*\*\s*exchange_rate",
            r"exchange_rate.*\*\s*saka",
        ]
        
        violations = []
        
        # Scanner tous les fichiers Python du backend
        for py_file in backend_dir.rglob("*.py"):
            # Ignorer les tests et migrations
            if "test" in str(py_file) or "migration" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        violations.append({
                            "file": str(py_file.relative_to(backend_dir.parent)),
                            "line": content[:match.start()].count("\n") + 1,
                            "pattern": pattern,
                            "match": match.group(0)[:50],
                        })
            except (UnicodeDecodeError, PermissionError):
                # Ignorer les fichiers non lisibles
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} fonction(s) de conversion SAKA ↔ EUR détectée(s).\n"
            f"La structure relationnelle (SAKA) doit toujours primer sur la structure instrumentale (EUR).\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )
    
    def test_saka_jamais_affiche_comme_monnaie(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        SAKA est affiché avec un symbole monétaire.
        
        Test : Scanner le code frontend pour détecter les affichages monétaires.
        """
        frontend_dir = Path(__file__).parent.parent.parent.parent.parent / "frontend" / "frontend"
        
        # Patterns interdits pour affichage monétaire
        forbidden_patterns = [
            r"saka.*€",
            r"saka.*\$",
            r"saka.*USD",
            r"saka.*EUR",
            r"saka.*GBP",
            r"formatSakaAmount.*€",
            r"formatSakaAmount.*\$",
            r"sakaBalance.*€",
            r"sakaBalance.*\$",
        ]
        
        violations = []
        
        # Scanner tous les fichiers JS/JSX/TS/TSX du frontend
        for js_file in frontend_dir.rglob("*.{js,jsx,ts,tsx}"):
            # Ignorer les tests et node_modules
            if "test" in str(js_file) or "node_modules" in str(js_file):
                continue
            
            try:
                content = js_file.read_text(encoding="utf-8")
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        # Vérifier que ce n'est pas dans un commentaire
                        before_match = content[:match.start()]
                        # Compter les commentaires avant le match
                        comment_count = before_match.count("//") + before_match.count("/*")
                        # Si le nombre de commentaires est impair, on est dans un commentaire
                        if comment_count % 2 == 1:
                            continue
                        
                        violations.append({
                            "file": str(js_file.relative_to(frontend_dir.parent.parent)),
                            "line": content[:match.start()].count("\n") + 1,
                            "pattern": pattern,
                            "match": match.group(0)[:50],
                        })
            except (UnicodeDecodeError, PermissionError):
                # Ignorer les fichiers non lisibles
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} affichage(s) monétaire(s) du SAKA détecté(s).\n"
            f"Le SAKA doit être affiché en 'grains', jamais avec un symbole monétaire (€, $, etc.).\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )
    
    def test_structure_relationnelle_prioritaire(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        La structure instrumentale (EUR) prime sur la structure relationnelle (SAKA).
        
        Test : Vérifier que les services SAKA ne dépendent pas des services EUR.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        saka_service = backend_dir / "core" / "services" / "saka.py"
        
        if not saka_service.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'core/services/saka.py' est introuvable. "
                f"Chemin attendu : {saka_service}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la dépendance SAKA/EUR ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        content = saka_service.read_text(encoding="utf-8")
        
        # Vérifier qu'aucun import de services financiers
        forbidden_imports = [
            "from finance.services import",
            "from finance import",
            "import finance.services",
            "from finance.models import UserWallet",
        ]
        
        violations = []
        
        for forbidden in forbidden_imports:
            if forbidden.lower() in content.lower():
                violations.append(forbidden)
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le service SAKA importe des services financiers.\n"
            f"La structure relationnelle (SAKA) doit être indépendante de la structure instrumentale (EUR).\n\n"
            f"Imports interdits détectés :\n" +
            "\n".join([f"  - {v}" for v in violations])
        )

