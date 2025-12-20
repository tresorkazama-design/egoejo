"""
Tests de conformité : Cycle SAKA incompressible

PHILOSOPHIE EGOEJO :
- Le cycle SAKA (Récolte → Usage → Compost → Silo → Redistribution) est NON NÉGOCIABLE
- Le compostage ne peut pas être désactivé, contourné ou supprimé
- Le Silo DOIT être alimenté après compost

Ces tests vérifient que le cycle SAKA est respecté dans le code.
"""
import re
from pathlib import Path
import pytest
from django.test import override_settings
from django.utils import timezone
from datetime import timedelta

from core.models.saka import SakaWallet, SakaSilo, SakaCompostLog
from core.services.saka import run_saka_compost_cycle


class TestSakaCycleIncompressible:
    """
    Tests de conformité : Vérification que le cycle SAKA est incompressible
    """
    
    @pytest.fixture
    def saka_service_path(self):
        """Chemin vers le service SAKA"""
        return Path(__file__).parent.parent.parent / "core" / "services" / "saka.py"
    
    def test_compostage_ne_peut_pas_etre_desactive(self, saka_service_path):
        """
        Vérifie qu'il n'existe aucune logique permettant de désactiver le compostage.
        
        RÈGLE ABSOLUE : Le compostage SAKA ne peut pas être désactivé.
        Le cycle SAKA est NON NÉGOCIABLE.
        """
        if not saka_service_path.exists():
            pytest.skip(f"Fichier non trouvé : {saka_service_path}")
        
        with open(saka_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns interdits : désactivation du compostage
        # Plus précis : chercher des patterns de désactivation explicite (pas les feature flags)
        # Exclure les vérifications de feature flags (SAKA_COMPOST_ENABLED est autorisé)
        
        # Exclure d'abord les lignes qui contiennent des vérifications de feature flags légitimes
        lines_to_exclude = set()
        for i, line in enumerate(content.split('\n'), 1):
            # Exclure les vérifications de feature flags (SAKA_COMPOST_ENABLED)
            if 'SAKA_COMPOST_ENABLED' in line or ('getattr' in line and 'settings' in line):
                lines_to_exclude.add(i)
        
        forbidden_patterns = [
            r'disable.*compost|compost.*disable',  # Désactivation du compostage
            r'skip.*compost|compost.*skip',  # Contournement du compostage
            r'bypass.*compost|compost.*bypass',  # Bypass du compostage
            r'remove.*compost|compost.*remove',  # Suppression du compostage
            r'if.*user.*skip.*compost|if.*skip.*compost',  # Condition pour éviter le compostage
            r'if.*user.*bypass.*compost|if.*bypass.*compost',  # Condition pour bypass
            r'compost.*=.*False|compost.*=.*None',  # Désactivation explicite
        ]
        
        # Exclure les signatures de fonctions (def run_saka_compost_cycle, etc.)
        function_signatures = set()
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip().startswith('def ') and 'compost' in line.lower():
                function_signatures.add(i)
        
        violations = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                # Exclure les lignes de vérification de feature flags légitimes et les signatures de fonctions
                if line_num not in lines_to_exclude and line_num not in function_signatures:
                    violations.append(f"Ligne {line_num}: {match.group()}")
        
        assert len(violations) == 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Désactivation/contournement du compostage détecté dans {saka_service_path.name}.\n"
            f"Violations trouvées :\n" + "\n".join(violations) + "\n\n"
            f"ACTION REQUISE : Le compostage SAKA est NON NÉGOCIABLE. Supprimer toute logique de désactivation."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_COMPOST_ENABLED=True,
        SAKA_COMPOST_INACTIVITY_DAYS=90,
        SAKA_COMPOST_RATE=0.1,
        SAKA_COMPOST_MIN_BALANCE=50,
        SAKA_COMPOST_MIN_AMOUNT=10,
    )
    def test_silo_doit_etre_alimente_apres_compost(self):
        """
        Vérifie que le Silo Commun est alimenté après un cycle de compostage.
        
        RÈGLE ABSOLUE : Le SAKA composté DOIT retourner au Silo Commun.
        Le Silo est la destination finale du SAKA inactif.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Créer un utilisateur avec un wallet inactif
        user = User.objects.create_user(
            username='test_inactif',
            email='test_inactif@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 200,
                'total_harvested': 200,
                'total_planted': 0,
                'last_activity_date': timezone.now() - timedelta(days=120),  # Inactif depuis 120 jours
            }
        )
        wallet.balance = 200
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        # Récupérer ou créer le Silo
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        silo_initial_balance = silo.total_balance
        silo_initial_composted = silo.total_composted
        
        # Exécuter le cycle de compostage
        result = run_saka_compost_cycle(dry_run=False, source="test")
        
        # Vérifier que le compostage a eu lieu
        assert result['total_composted'] > 0, (
            "VIOLATION CONSTITUTION EGOEJO : Le compostage n'a pas eu lieu alors qu'un wallet est éligible."
        )
        
        # Rafraîchir le Silo depuis la base de données
        silo.refresh_from_db()
        
        # Vérifier que le Silo a été alimenté
        assert silo.total_balance > silo_initial_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : Le Silo Commun n'a pas été alimenté après compostage.\n"
            f"Solde initial : {silo_initial_balance}\n"
            f"Solde après compost : {silo.total_balance}\n"
            f"SAKA composté : {result['total_composted']}\n\n"
            f"ACTION REQUISE : Le SAKA composté DOIT retourner au Silo Commun."
        )
        
        # Vérifier que le total composté a augmenté
        assert silo.total_composted > silo_initial_composted, (
            f"VIOLATION CONSTITUTION EGOEJO : Le total composté du Silo n'a pas augmenté.\n"
            f"Total initial : {silo_initial_composted}\n"
            f"Total après compost : {silo.total_composted}\n\n"
            f"ACTION REQUISE : Le total composté du Silo DOIT être mis à jour."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_COMPOST_ENABLED=True,
        SAKA_COMPOST_INACTIVITY_DAYS=90,
        SAKA_COMPOST_RATE=0.1,
        SAKA_COMPOST_MIN_BALANCE=50,
        SAKA_COMPOST_MIN_AMOUNT=10,
    )
    def test_cycle_saka_incompressible(self):
        """
        Vérifie que le cycle SAKA complet est incompressible.
        
        RÈGLE ABSOLUE : Le cycle SAKA (Récolte → Usage → Compost → Silo → Redistribution) est NON NÉGOCIABLE.
        Aucune étape ne peut être supprimée ou contournée.
        """
        from django.contrib.auth import get_user_model
        from core.services.saka import harvest_saka, spend_saka, SakaReason
        User = get_user_model()
        
        # Créer un utilisateur
        user = User.objects.create_user(
            username='test_cycle',
            email='test_cycle@example.com',
            password='testpass123'
        )
        
        # Récupérer ou créer le wallet
        from core.services.saka import get_or_create_wallet
        wallet = get_or_create_wallet(user)
        
        # ÉTAPE 1 : Récolte (Harvest)
        harvest_result = harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        assert harvest_result is not None, "La récolte SAKA doit fonctionner"
        
        # Rafraîchir le wallet depuis la base de données
        wallet.refresh_from_db()
        assert wallet.balance == 100, "Le solde doit être crédité après récolte"
        
        # ÉTAPE 2 : Usage (Spend)
        spend_result = spend_saka(user, 30, "test_spend")
        assert spend_result is True, "La dépense SAKA doit fonctionner"
        
        wallet.refresh_from_db()
        assert wallet.balance == 70, "Le solde doit être débité après dépense"
        
        # ÉTAPE 3 : Compost (simuler inactivité)
        # S'assurer que le wallet a un solde suffisant (min_balance = 50) et est inactif
        wallet.balance = 100  # Solde suffisant pour le compostage
        wallet.last_activity_date = timezone.now() - timedelta(days=120)  # Inactif depuis 120 jours
        wallet.save()
        
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        silo_initial = silo.total_balance
        
        compost_result = run_saka_compost_cycle(dry_run=False, source="test")
        assert compost_result['total_composted'] > 0, "Le compostage doit avoir lieu"
        
        # ÉTAPE 4 : Silo alimenté
        silo.refresh_from_db()
        assert silo.total_balance > silo_initial, (
            "VIOLATION CONSTITUTION EGOEJO : Le Silo Commun DOIT être alimenté après compostage.\n"
            "Le cycle SAKA est incomplet si le Silo n'est pas alimenté."
        )
        
        # Vérifier que le wallet a été débité
        wallet.refresh_from_db()
        # Le wallet avait 100 grains, après compost (10% = 10 grains), il devrait avoir 90 grains
        assert wallet.balance < 100, (
            f"VIOLATION CONSTITUTION EGOEJO : Le wallet inactif DOIT être débité après compostage.\n"
            f"Solde avant compost : 100, Solde après compost : {wallet.balance}.\n"
            f"Le compostage est une étape obligatoire du cycle SAKA."
        )
        assert wallet.balance == 90, (
            f"VIOLATION CONSTITUTION EGOEJO : Le wallet n'a pas été correctement débité après compostage.\n"
            f"Solde attendu : 90 (100 - 10%), Solde actuel : {wallet.balance}.\n"
            f"Le compostage doit prélever 10% du solde."
        )
        
        # Vérifier qu'un log de compostage a été créé
        compost_logs = SakaCompostLog.objects.filter(
            total_composted__gt=0
        ).order_by('-started_at')
        assert compost_logs.exists(), (
            "VIOLATION CONSTITUTION EGOEJO : Un log de compostage DOIT être créé.\n"
            "La traçabilité du cycle SAKA est obligatoire."
        )

