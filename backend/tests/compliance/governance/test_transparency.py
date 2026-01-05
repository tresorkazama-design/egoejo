"""
EGOEJO Compliance Test : Transparence des Métriques

LOI EGOEJO :
"Les scores et métriques doivent être présentés honnêtement avec leurs métadonnées."

Ce test vérifie que :
- Aucun score n'est présenté comme "objectif" sans métadonnées
- Les métriques sont documentées
- Aucune métrique fake n'est utilisée

Violation du Manifeste EGOEJO si :
- Un score est présenté comme "objectif" sans métadonnées
- Une métrique est fake ou arbitraire
- Les métadonnées sont absentes
"""
import pytest
import re
from pathlib import Path


@pytest.mark.egoejo_compliance
class TestTransparency:
    """
    Tests de conformité : Transparence des Métriques
    
    RÈGLE ABSOLUE : Les scores et métriques doivent être présentés honnêtement.
    """
    
    def test_aucun_score_objectif_sans_metadonnees(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un score est présenté comme "objectif" sans métadonnées.
        
        Test : Scanner le code pour détecter les scores "objectifs" sans documentation.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        frontend_dir = Path(__file__).parent.parent.parent.parent.parent / "frontend" / "frontend"
        
        # Patterns suspects pour scores "objectifs" sans métadonnées
        suspicious_patterns = [
            r"score.*objectif",
            r"objective.*score",
            r"score.*\*\s*random",
            r"random.*score",
            r"#.*fake.*score",
            r"#.*arbitrary.*score",
        ]
        
        violations = []
        
        # Scanner les fichiers backend
        for py_file in backend_dir.rglob("*.py"):
            # Exclure les tests, migrations, et dépendances (venv, site-packages)
            if ("test" in str(py_file) or 
                "migration" in str(py_file) or 
                "venv" in str(py_file) or 
                "site-packages" in str(py_file) or
                ".venv" in str(py_file)):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                for pattern in suspicious_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Vérifier que ce n'est pas dans un commentaire explicatif
                        before_match = content[:match.start()]
                        # Chercher des métadonnées dans les 10 lignes précédentes
                        lines_before = before_match.split("\n")[-10:]
                        has_metadata = any(
                            "metadata" in line.lower() or
                            "metadonnee" in line.lower() or
                            "documentation" in line.lower() or
                            "#" in line  # Commentaire explicatif
                            for line in lines_before
                        )
                        
                        if not has_metadata:
                            violations.append({
                                "file": str(py_file.relative_to(backend_dir.parent)),
                                "line": content[:match.start()].count("\n") + 1,
                                "match": match.group(0)[:50],
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Scanner les fichiers frontend
        for js_file in frontend_dir.rglob("*.{js,jsx,ts,tsx}"):
            # Exclure les tests et dépendances
            if ("test" in str(js_file) or 
                "node_modules" in str(js_file) or
                ".venv" in str(js_file)):
                continue
            
            try:
                content = js_file.read_text(encoding="utf-8")
                
                for pattern in suspicious_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Vérifier que ce n'est pas dans un commentaire
                        before_match = content[:match.start()]
                        comment_count = before_match.count("//") + before_match.count("/*")
                        if comment_count % 2 == 1:
                            continue
                        
                        # Chercher des métadonnées
                        lines_before = before_match.split("\n")[-10:]
                        has_metadata = any(
                            "metadata" in line.lower() or
                            "metadonnee" in line.lower() or
                            "documentation" in line.lower() or
                            "//" in line or "/*" in line
                            for line in lines_before
                        )
                        
                        if not has_metadata:
                            violations.append({
                                "file": str(js_file.relative_to(frontend_dir.parent.parent)),
                                "line": content[:match.start()].count("\n") + 1,
                                "match": match.group(0)[:50],
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} score(s) 'objectif(s)' sans métadonnées détecté(s).\n"
            f"Les scores doivent être présentés honnêtement avec leurs métadonnées.\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )
    
    def test_aucune_metrique_fake(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une métrique fake ou arbitraire est utilisée.
        
        Test : Scanner le code pour détecter les métriques suspectes.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        
        # Patterns interdits pour métriques fake
        forbidden_patterns = [
            r"#.*fake.*metric",
            r"#.*arbitrary.*metric",
            r"metric.*\*\s*random",
            r"random.*metric",
            r"fake.*score",
            r"dummy.*metric",
        ]
        
        violations = []
        
        for py_file in backend_dir.rglob("*.py"):
            # Exclure les tests, migrations, et dépendances (venv, site-packages)
            if ("test" in str(py_file) or 
                "migration" in str(py_file) or 
                "venv" in str(py_file) or 
                "site-packages" in str(py_file) or
                ".venv" in str(py_file)):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        violations.append({
                            "file": str(py_file.relative_to(backend_dir.parent)),
                            "line": content[:match.start()].count("\n") + 1,
                            "match": match.group(0)[:50],
                        })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} métrique(s) fake ou arbitraire(s) détectée(s).\n"
            f"Les métriques doivent être honnêtes et documentées.\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )

