"""
EGOEJO Compliance Test : Séparation des Modèles SAKA / EUR

LOI EGOEJO :
"Les modèles SAKA et EUR doivent être strictement séparés. Aucune relation directe n'est autorisée."

Ce test vérifie que :
- SakaWallet et UserWallet sont des modèles distincts
- Aucune ForeignKey ne lie SakaWallet et UserWallet
- Aucun champ commun ne permet la conversion

Violation du Manifeste EGOEJO si :
- Une ForeignKey lie SakaWallet et UserWallet
- Un champ permet la conversion SAKA ↔ EUR
- Les modèles sont fusionnés ou liés directement
"""
import pytest
from django.apps import apps
from django.db import models


@pytest.mark.egoejo_compliance
class TestModelsSeparation:
    """
    Tests de conformité : Séparation des Modèles SAKA / EUR
    
    RÈGLE ABSOLUE : Les modèles SAKA et EUR doivent être strictement séparés.
    """
    
    def test_saka_wallet_et_user_wallet_separes(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        SakaWallet et UserWallet sont liés par une ForeignKey.
        
        Test : Vérifier qu'aucune ForeignKey ne lie les deux modèles.
        """
        try:
            SakaWallet = apps.get_model('core', 'SakaWallet')
            UserWallet = apps.get_model('finance', 'UserWallet')
        except LookupError as e:
            pytest.fail(
                f"PROTECTION MANQUANTE : Les modèles critiques SakaWallet ou UserWallet sont introuvables. "
                f"Erreur : {e}. "
                f"Ces modèles sont OBLIGATOIRES pour la conformité EGOEJO. "
                f"Sans ces modèles, les protections contre la fusion SAKA/EUR ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        # Vérifier que SakaWallet n'a pas de ForeignKey vers UserWallet
        saka_fields = SakaWallet._meta.get_fields()
        
        violations = []
        
        for field in saka_fields:
            if isinstance(field, models.ForeignKey):
                related_model = field.related_model
                if related_model == UserWallet:
                    violations.append(f"SakaWallet.{field.name} → UserWallet")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} ForeignKey(s) liant SakaWallet et UserWallet détectée(s).\n"
            f"Les modèles SAKA et EUR doivent être strictement séparés.\n\n"
            f"Violations détectées :\n" +
            "\n".join([f"  - {v}" for v in violations])
        )
    
    def test_aucun_champ_conversion_saka_eur(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un champ permet la conversion SAKA ↔ EUR.
        
        Test : Vérifier qu'aucun champ ne contient "conversion", "exchange_rate", etc.
        """
        try:
            SakaWallet = apps.get_model('core', 'SakaWallet')
        except LookupError as e:
            pytest.fail(
                f"PROTECTION MANQUANTE : Le modèle critique SakaWallet est introuvable. "
                f"Erreur : {e}. "
                f"Ce modèle est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce modèle, les protections contre la conversion SAKA/EUR ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        # Patterns interdits pour les noms de champs
        forbidden_patterns = [
            'conversion',
            'exchange_rate',
            'eur_equivalent',
            'value_in_eur',
            'price_in_eur',
        ]
        
        violations = []
        
        for field in SakaWallet._meta.get_fields():
            field_name = field.name.lower()
            
            for pattern in forbidden_patterns:
                if pattern in field_name:
                    violations.append(f"SakaWallet.{field.name}")
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : {len(violations)} champ(s) suspect(s) de conversion détecté(s).\n"
            f"Aucun champ ne doit permettre la conversion SAKA ↔ EUR.\n\n"
            f"Violations détectées :\n" +
            "\n".join([f"  - {v}" for v in violations])
        )
    
    def test_saka_wallet_independant_user_wallet(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        SakaWallet dépend directement de UserWallet.
        
        Test : Vérifier que SakaWallet n'importe pas UserWallet.
        """
        from pathlib import Path
        import re
        
        backend_dir = Path(__file__).parent.parent.parent.parent.parent / "backend"
        saka_models = backend_dir / "core" / "models" / "saka.py"
        
        if not saka_models.exists():
            pytest.fail(
                f"PROTECTION MANQUANTE : Le fichier critique 'core/models/saka.py' est introuvable. "
                f"Chemin attendu : {saka_models}. "
                f"Ce fichier est OBLIGATOIRE pour la conformité EGOEJO. "
                f"Sans ce fichier, les protections contre la fusion SAKA/EUR ne peuvent pas être vérifiées. "
                f"Conformité EGOEJO VIOLÉE."
            )
        
        content = saka_models.read_text(encoding="utf-8")
        
        # Vérifier qu'aucun import de UserWallet
        forbidden_imports = [
            "from finance.models import UserWallet",
            "from finance import UserWallet",
            "import finance.models.UserWallet",
        ]
        
        violations = []
        
        for forbidden in forbidden_imports:
            if forbidden.lower() in content.lower():
                violations.append(forbidden)
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le modèle SakaWallet importe UserWallet.\n"
            f"Les modèles SAKA et EUR doivent être indépendants.\n\n"
            f"Imports interdits détectés :\n" +
            "\n".join([f"  - {v}" for v in violations])
        )

