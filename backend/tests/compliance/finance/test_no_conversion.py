"""
EGOEJO Compliance Test : Aucune Conversion SAKA ↔ EUR

LOI EGOEJO :
"Aucune conversion SAKA ↔ EUR n'est autorisée. SAKA et EUR sont strictement séparés."

Ce test vérifie que :
- Aucune fonction de conversion n'existe
- Aucun endpoint API de conversion n'existe
- Aucun mécanisme de conversion n'est possible

Violation du Manifeste EGOEJO si :
- Une fonction convert_saka_to_eur() existe
- Un endpoint /api/saka/convert/ existe
- Un mécanisme de conversion est implémenté
"""
import pytest
import re
import json
import base64
from pathlib import Path


@pytest.mark.egoejo_compliance
class TestNoConversion:
    """
    Tests de conformité : Aucune Conversion SAKA ↔ EUR
    
    RÈGLE ABSOLUE : Aucune conversion SAKA ↔ EUR n'est autorisée.
    """
    
    def test_aucune_fonction_conversion_dans_code(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une fonction de conversion SAKA ↔ EUR existe dans le code.
        
        Test : Scanner le code pour détecter les fonctions de conversion.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        patterns_file = Path(__file__).parent.parent.parent / "test_patterns.json"
        
        # Charger les patterns depuis test_patterns.json
        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                patterns_data = json.load(f)
            
            # Décoder les patterns Base64
            conv_encoded = patterns_data.get('conv_enc', [])
            compiled_patterns = []
            
            for enc_pattern in conv_encoded:
                try:
                    decoded = base64.b64decode(enc_pattern).decode('utf-8')
                    compiled_patterns.append(re.compile(decoded, re.IGNORECASE))
                except (base64.binascii.Error, UnicodeDecodeError):
                    continue
        else:
            # Patterns de fallback si le fichier n'existe pas
            compiled_patterns = [
                re.compile(r"def\s+convert.*saka.*eur", re.IGNORECASE),
                re.compile(r"def\s+convert.*eur.*saka", re.IGNORECASE),
                re.compile(r"def\s+saka.*to.*eur", re.IGNORECASE),
                re.compile(r"def\s+eur.*to.*saka", re.IGNORECASE),
            ]
        
        violations = []
        
        # Scanner tous les fichiers Python du backend
        for py_file in backend_dir.rglob("*.py"):
            # Ignorer les tests et migrations
            if "test" in str(py_file) or "migration" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                for pattern in compiled_patterns:
                    matches = pattern.finditer(content)
                    for match in matches:
                        violations.append({
                            "file": str(py_file.relative_to(backend_dir.parent)),
                            "line": content[:match.start()].count("\n") + 1,
                            "match": match.group(0)[:50],
                        })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} fonction(s) de conversion SAKA ↔ EUR détectée(s).\n"
            f"Aucune conversion SAKA ↔ EUR n'est autorisée.\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )
    
    def test_aucun_endpoint_api_conversion(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un endpoint API permet la conversion SAKA ↔ EUR.
        
        Test : Scanner les URLs pour détecter les endpoints de conversion.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        
        # Patterns interdits pour les endpoints
        forbidden_patterns = [
            r"convert",
            r"exchange",
            r"rate.*eur",
            r"eur.*rate",
        ]
        
        violations = []
        
        # Scanner les fichiers urls.py
        for urls_file in backend_dir.rglob("**/urls.py"):
            try:
                content = urls_file.read_text(encoding="utf-8")
                
                for pattern in forbidden_patterns:
                    # Chercher dans les path() ou url() patterns
                    url_pattern = re.compile(
                        rf"(?:path|url)\(['\"].*{pattern}.*['\"]",
                        re.IGNORECASE
                    )
                    matches = url_pattern.finditer(content)
                    
                    for match in matches:
                        # Vérifier que ce n'est pas un endpoint autorisé (ex: "rate_limiting")
                        if "rate_limiting" not in match.group(0).lower():
                            violations.append({
                                "file": str(urls_file.relative_to(backend_dir.parent)),
                                "line": content[:match.start()].count("\n") + 1,
                                "match": match.group(0)[:50],
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} endpoint(s) API de conversion détecté(s).\n"
            f"Aucun endpoint API ne peut permettre la conversion SAKA ↔ EUR.\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )
    
    def test_aucun_mecanisme_conversion(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un mécanisme de conversion est implémenté (même indirect).
        
        Test : Vérifier qu'aucun service ne calcule un taux de conversion.
        """
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        
        # Patterns interdits pour les mécanismes de conversion
        forbidden_patterns = [
            r"exchange_rate",
            r"conversion_rate",
            r"saka.*price",
            r"saka.*value.*eur",
            r"calculate.*saka.*eur",
        ]
        
        violations = []
        
        # Scanner les fichiers de services
        for service_file in backend_dir.rglob("**/services/*.py"):
            try:
                content = service_file.read_text(encoding="utf-8")
                
                for pattern in forbidden_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Vérifier que ce n'est pas dans un commentaire
                        before_match = content[:match.start()]
                        comment_count = before_match.count("#") + before_match.count('"""') + before_match.count("'''")
                        if comment_count % 2 == 1:
                            continue
                        
                        violations.append({
                            "file": str(service_file.relative_to(backend_dir.parent)),
                            "line": content[:match.start()].count("\n") + 1,
                            "match": match.group(0)[:50],
                        })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} mécanisme(s) de conversion détecté(s).\n"
            f"Aucun mécanisme de conversion SAKA ↔ EUR n'est autorisé.\n\n"
            f"Violations détectées :\n" +
            "\n".join([
                f"  - {v['file']}:{v['line']} : {v['match']}"
                for v in violations[:10]  # Limiter à 10 pour lisibilité
            ])
        )

