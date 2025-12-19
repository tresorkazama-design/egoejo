"""
Test P0 CRITIQUE : Étanchéité SAKA/EUR - Aucune fonction ne lie UserWallet à SakaWallet

PHILOSOPHIE EGOEJO :
La structure relationnelle (SAKA) et la structure instrumentale (EUR) sont strictement séparées.
Aucune fonction ne doit créer de lien entre UserWallet (EUR) et SakaWallet (SAKA).

Ce test protège la règle : "Séparation stricte SAKA/EUR - Aucune fonction ne lie UserWallet à SakaWallet"

VIOLATION EMPÊCHÉE :
- Fonction qui prend UserWallet et retourne SakaWallet
- Fonction qui prend SakaWallet et retourne UserWallet
- Fonction qui modifie UserWallet basé sur SakaWallet
- Fonction qui modifie SakaWallet basé sur UserWallet
- ForeignKey ou relation directe entre UserWallet et SakaWallet
"""
import pytest
import re
from pathlib import Path
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from finance.models import UserWallet
from core.models.saka import SakaWallet

User = get_user_model()


class TestSakaEurEtancheite:
    """
    Tests pour garantir l'étanchéité entre SAKA et EUR.
    
    PROTECTION : Empêche toute liaison entre UserWallet (EUR) et SakaWallet (SAKA).
    VIOLATION EMPÊCHÉE : Conversion implicite, liaison fonctionnelle, corruption structurelle.
    """
    
    def test_aucune_fonction_lie_userwallet_sakawallet(self):
        """
        Test P0 : Aucune fonction ne lie UserWallet à SakaWallet.
        
        Ce test protège la règle : "Séparation stricte SAKA/EUR - Aucune fonction ne lie UserWallet à SakaWallet"
        
        Vérifie que :
        - Aucune fonction ne prend UserWallet et retourne SakaWallet
        - Aucune fonction ne prend SakaWallet et retourne UserWallet
        - Aucune fonction ne modifie UserWallet basé sur SakaWallet
        - Aucune fonction ne modifie SakaWallet basé sur UserWallet
        """
        # Scanner les fichiers de services
        service_files = [
            Path(__file__).parent.parent.parent / "finance" / "services.py",
            Path(__file__).parent.parent.parent / "core" / "services" / "saka.py",
            Path(__file__).parent.parent.parent / "core" / "api" / "saka_views.py",
            Path(__file__).parent.parent.parent / "core" / "api" / "impact_views.py",
        ]
        
        violations = []
        
        for service_file in service_files:
            if not service_file.exists():
                continue
            
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patterns interdits : fonctions qui lient UserWallet et SakaWallet
            forbidden_patterns = [
                # Fonction qui prend UserWallet et retourne SakaWallet
                r'def\s+\w+.*UserWallet.*SakaWallet|def\s+\w+.*user_wallet.*saka_wallet',
                # Fonction qui prend SakaWallet et retourne UserWallet
                r'def\s+\w+.*SakaWallet.*UserWallet|def\s+\w+.*saka_wallet.*user_wallet',
                # Fonction qui modifie UserWallet basé sur SakaWallet
                r'UserWallet.*balance.*\+=.*SakaWallet|user_wallet.*balance.*\+=.*saka_wallet',
                r'UserWallet.*balance.*-=.*SakaWallet|user_wallet.*balance.*-=.*saka_wallet',
                # Fonction qui modifie SakaWallet basé sur UserWallet
                r'SakaWallet.*balance.*\+=.*UserWallet|saka_wallet.*balance.*\+=.*user_wallet',
                r'SakaWallet.*balance.*-=.*UserWallet|saka_wallet.*balance.*-=.*user_wallet',
                # Conversion implicite
                r'convert.*user.*wallet.*saka|convert.*saka.*user.*wallet',
                r'user.*wallet.*to.*saka|saka.*to.*user.*wallet',
            ]
            
            for pattern in forbidden_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    
                    # Exclure les commentaires et docstrings
                    if not line_content.startswith('#') and '"""' not in line_content:
                        violations.append(
                            f"{service_file.name} (ligne {line_num}): {line_content[:80]}"
                        )
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Fonction(s) liant UserWallet et SakaWallet détectée(s).\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute fonction créant un lien entre UserWallet (EUR) et SakaWallet (SAKA). "
            f"La séparation stricte SAKA/EUR est NON NÉGOCIABLE."
        )
    
    def test_aucune_relation_directe_userwallet_sakawallet(self):
        """
        Test P0 : Aucune relation directe (ForeignKey, OneToOne) entre UserWallet et SakaWallet.
        
        Ce test protège la règle : "Séparation stricte SAKA/EUR - Aucune fonction ne lie UserWallet à SakaWallet"
        
        Vérifie que :
        - UserWallet n'a pas de ForeignKey vers SakaWallet
        - SakaWallet n'a pas de ForeignKey vers UserWallet
        - Aucune relation OneToOne entre les deux
        """
        # Vérifier les modèles
        user_wallet_fields = [f.name for f in UserWallet._meta.get_fields()]
        saka_wallet_fields = [f.name for f in SakaWallet._meta.get_fields()]
        
        # Vérifier qu'aucun champ ne référence l'autre modèle
        forbidden_user_wallet_fields = ['saka_wallet', 'sakawallet', 'saka']
        forbidden_saka_wallet_fields = ['user_wallet', 'userwallet', 'eur_wallet', 'eurwallet']
        
        violations = []
        
        for field in forbidden_user_wallet_fields:
            if field in user_wallet_fields:
                violations.append(f"UserWallet contient un champ '{field}' référençant SakaWallet")
        
        for field in forbidden_saka_wallet_fields:
            if field in saka_wallet_fields:
                violations.append(f"SakaWallet contient un champ '{field}' référençant UserWallet")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Relation directe entre UserWallet et SakaWallet détectée.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Supprimer toute relation directe entre UserWallet (EUR) et SakaWallet (SAKA). "
            f"La séparation stricte SAKA/EUR est NON NÉGOCIABLE."
        )
    
    @pytest.mark.django_db
    def test_aucune_modification_croisee_userwallet_sakawallet(self):
        """
        Test P0 : Aucune modification croisée UserWallet ↔ SakaWallet.
        
        Ce test protège la règle : "Séparation stricte SAKA/EUR - Aucune fonction ne lie UserWallet à SakaWallet"
        
        Vérifie que :
        - Modifier UserWallet ne modifie pas SakaWallet
        - Modifier SakaWallet ne modifie pas UserWallet
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer UserWallet et SakaWallet
        user_wallet, _ = UserWallet.objects.get_or_create(user=user)
        user_wallet.balance = Decimal('1000.00')
        user_wallet.save()
        
        saka_wallet, _ = SakaWallet.objects.get_or_create(user=user)
        saka_wallet.balance = 200
        saka_wallet.save()
        
        # État initial
        initial_user_wallet_balance = user_wallet.balance
        initial_saka_wallet_balance = saka_wallet.balance
        
        # Modifier UserWallet
        user_wallet.balance = Decimal('1500.00')
        user_wallet.save()
        
        # Vérifier que SakaWallet n'a PAS changé
        saka_wallet.refresh_from_db()
        assert saka_wallet.balance == initial_saka_wallet_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : Modification de UserWallet a affecté SakaWallet. "
            f"Balance SakaWallet initiale: {initial_saka_wallet_balance}, "
            f"Balance SakaWallet après modification UserWallet: {saka_wallet.balance}"
        )
        
        # Modifier SakaWallet
        saka_wallet.balance = 300
        saka_wallet.save()
        
        # Vérifier que UserWallet n'a PAS changé
        user_wallet.refresh_from_db()
        assert user_wallet.balance == Decimal('1500.00'), (
            f"VIOLATION CONSTITUTION EGOEJO : Modification de SakaWallet a affecté UserWallet. "
            f"Balance UserWallet attendue: 1500.00, "
            f"Balance UserWallet après modification SakaWallet: {user_wallet.balance}"
        )

