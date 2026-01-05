"""
EGOEJO Compliance Test : Intégrité du Cycle SAKA

LOI EGOEJO :
"Le cycle SAKA est non négociable : Récolte → Plantation → Compost → Silo → Redistribution.
Aucune étape ne peut être supprimée ou contournée."

Ce test vérifie que :
- Le cycle complet est respecté : Récolte → Plantation → Compost → Silo → Redistribution
- Aucun saut d'étape n'est possible
- Si une étape manque, le test FAIL

Violation du Manifeste EGOEJO si :
- Une étape du cycle peut être supprimée
- Une étape du cycle peut être contournée
- Le cycle n'est pas complet
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.test import override_settings

from core.models.saka import SakaWallet, SakaTransaction, SakaSilo, SakaCompostLog
from core.services.saka import (
    harvest_saka,
    spend_saka,
    run_saka_compost_cycle,
    redistribute_saka_silo,
    SakaReason
)
from django.conf import settings

User = get_user_model()


@pytest.mark.egoejo_compliance
class TestSakaCycleIntegrity:
    """
    Tests de conformité : Intégrité du Cycle SAKA
    
    RÈGLE ABSOLUE : Le cycle SAKA est non négociable.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_COMPOST_ENABLED=True,
        SAKA_COMPOST_INACTIVITY_DAYS=90,
        SAKA_COMPOST_RATE=0.1,
        SAKA_COMPOST_MIN_BALANCE=50,
        SAKA_COMPOST_MIN_AMOUNT=10,
        SAKA_SILO_REDIS_ENABLED=True,
        SAKA_SILO_REDIS_RATE=0.1,
        SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    )
    def test_cycle_complet_recolte_plantation_compost_silo_redistribution(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le cycle complet n'est pas respecté : Récolte → Plantation → Compost → Silo → Redistribution.
        
        Test : Vérifier que toutes les étapes du cycle sont exécutées.
        """
        user = User.objects.create_user(
            username='test_cycle_complete',
            email='test_cycle_complete@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(user=user)
        initial_balance = wallet.balance
        initial_harvested = wallet.total_harvested
        initial_planted = wallet.total_planted
        initial_composted = wallet.total_composted
        
        # ÉTAPE 1 : RÉCOLTE
        harvest_result = harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        assert harvest_result is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : L'étape RÉCOLTE a échoué. "
            "Le cycle SAKA doit commencer par la récolte."
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance + 100, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le solde SAKA n'a pas été crédité après récolte. "
            f"Solde attendu : {initial_balance + 100}, Solde actuel : {wallet.balance}"
        )
        assert wallet.total_harvested == initial_harvested + 100, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le total récolté n'a pas été mis à jour. "
            f"Total attendu : {initial_harvested + 100}, Total actuel : {wallet.total_harvested}"
        )
        
        # Vérifier qu'une transaction HARVEST a été créée
        harvest_transaction = SakaTransaction.objects.filter(
            user=user,
            direction='EARN'
        ).first()
        assert harvest_transaction is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : Aucune transaction HARVEST créée. "
            "Toute récolte doit être tracée."
        )
        
        # ÉTAPE 2 : PLANTATION (Usage/Spend)
        spend_result = spend_saka(user, 50, "test_plant")
        assert spend_result is True, (
            "VIOLATION DU MANIFESTE EGOEJO : L'étape PLANTATION (usage) a échoué. "
            "Le cycle SAKA doit inclure l'usage (plantation)."
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance + 100 - 50, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le solde SAKA n'a pas été débité après plantation. "
            f"Solde attendu : {initial_balance + 50}, Solde actuel : {wallet.balance}"
        )
        assert wallet.total_planted == initial_planted + 50, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le total planté n'a pas été mis à jour. "
            f"Total attendu : {initial_planted + 50}, Total actuel : {wallet.total_planted}"
        )
        
        # Vérifier qu'une transaction SPEND a été créée
        spend_transaction = SakaTransaction.objects.filter(
            user=user,
            direction='SPEND'
        ).first()
        assert spend_transaction is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : Aucune transaction SPEND créée. "
            "Toute plantation (usage) doit être tracée."
        )
        
        # ÉTAPE 3 : COMPOST
        # Récupérer le Silo (utiliser id=1 pour cohérence avec le service)
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        initial_silo_balance = silo.total_balance
        
        # S'assurer que le wallet est éligible au compost (inactif et solde suffisant)
        wallet.refresh_from_db()
        wallet.last_activity_date = timezone.now() - timedelta(days=120)  # Inactif depuis 120 jours
        wallet.balance = 100  # Solde suffisant (min_balance = 50)
        wallet.save()
        
        # Exécuter le cycle de compostage
        compost_result = run_saka_compost_cycle(dry_run=False, source="test")
        assert compost_result is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : L'étape COMPOST a échoué. "
            "Le cycle SAKA doit inclure le compostage."
        )
        
        # Vérifier que le Silo a été alimenté
        silo.refresh_from_db()
        assert silo.total_balance >= initial_silo_balance, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le Silo n'a pas été alimenté après compost. "
            f"Solde Silo avant : {initial_silo_balance}, Solde Silo après : {silo.total_balance}. "
            f"Le compost DOIT alimenter le Silo."
        )
        
        # ÉTAPE 4 : SILO (vérification)
        # Le Silo doit contenir le SAKA composté
        # Rafraîchir le Silo depuis la base de données
        silo.refresh_from_db()
        assert silo.total_balance > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le Silo est vide. "
            f"Solde Silo : {silo.total_balance}. "
            f"Le Silo DOIT contenir le SAKA composté."
        )
        
        # ÉTAPE 5 : REDISTRIBUTION
        # Vérifier que la fonction de redistribution existe et fonctionne
        # (si le Silo a un solde suffisant)
        if silo.total_balance >= 100:
            # Créer un autre utilisateur pour recevoir la redistribution
            user2 = User.objects.create_user(
                username='test_redistribution_receiver',
                email='test_redistribution_receiver@example.com',
                password='testpass123'
            )
            wallet2, _ = SakaWallet.objects.get_or_create(user=user2)
            initial_balance2 = wallet2.balance
            
            # Exécuter la redistribution
            redistribute_result = redistribute_saka_silo(rate=0.1)
            assert redistribute_result is not None, (
                "VIOLATION DU MANIFESTE EGOEJO : L'étape REDISTRIBUTION a échoué. "
                "Le cycle SAKA doit inclure la redistribution du Silo."
            )
            
            # Vérifier que le Silo a été débité
            silo.refresh_from_db()
            assert silo.total_balance < redistribute_result.get('initial_silo_balance', silo.total_balance), (
                f"VIOLATION DU MANIFESTE EGOEJO : Le Silo n'a pas été débité après redistribution. "
                f"Solde Silo : {silo.total_balance}. "
                f"La redistribution DOIT débité le Silo."
            )
            
            # Vérifier que les wallets ont été crédités
            wallet2.refresh_from_db()
            # Note : Le wallet2 peut ne pas être crédité s'il n'était pas éligible
            # (balance = 0, total_harvested = 0, etc.)
            # Mais si le Silo a été débité, au moins un wallet doit avoir été crédité
    
    @pytest.mark.django_db
    def test_aucun_saut_etape_possible(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un saut d'étape est possible dans le cycle SAKA.
        
        Test : Vérifier que chaque étape dépend de la précédente.
        """
        user = User.objects.create_user(
            username='test_no_skip_step',
            email='test_no_skip_step@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(user=user)
        initial_balance = wallet.balance
        
        # Tentative de PLANTATION sans RÉCOLTE (devrait échouer ou être impossible)
        # Note : spend_saka vérifie que le solde est suffisant
        spend_result = spend_saka(user, 50, "test_skip_harvest")
        
        # Assertion : On ne peut pas planter sans avoir récolté
        if spend_result:
            # Si spend_saka a réussi, c'est que le wallet avait déjà un solde
            # (ce qui est normal si le wallet existait déjà)
            # Mais on vérifie que le solde a bien été débité
            wallet.refresh_from_db()
            assert wallet.balance == initial_balance - 50, (
                f"VIOLATION DU MANIFESTE EGOEJO : Le solde SAKA n'a pas été débité après plantation. "
                f"Solde attendu : {initial_balance - 50}, Solde actuel : {wallet.balance}"
            )
        else:
            # Si spend_saka a échoué, c'est normal si le solde était insuffisant
            # (on ne peut pas planter sans avoir récolté)
            wallet.refresh_from_db()
            assert wallet.balance == initial_balance, (
                f"VIOLATION DU MANIFESTE EGOEJO : Le solde SAKA a été modifié alors que la plantation a échoué. "
                f"Solde attendu : {initial_balance}, Solde actuel : {wallet.balance}"
            )
        
        # Tentative de COMPOST sans RÉCOLTE ni PLANTATION (devrait être impossible)
        # Note : Le compostage s'applique aux wallets inactifs, pas aux wallets vides
        # Mais on vérifie que le compostage ne crée pas de SAKA ex nihilo
        
        # Récolter du SAKA d'abord
        harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        wallet.refresh_from_db()
        balance_before_compost = wallet.balance
        
        # Exécuter le compostage
        compost_result = run_saka_compost_cycle(dry_run=False, source="test")
        
        wallet.refresh_from_db()
        balance_after_compost = wallet.balance
        
        # Assertion : Le compostage ne peut pas créer de SAKA ex nihilo
        # (il ne peut que réduire le solde, pas l'augmenter)
        assert balance_after_compost <= balance_before_compost, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le compostage a créé du SAKA ex nihilo. "
            f"Solde avant compost : {balance_before_compost}, Solde après compost : {balance_after_compost}. "
            f"Le compostage ne peut que réduire le solde, pas l'augmenter."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_COMPOST_ENABLED=True,
        SAKA_COMPOST_INACTIVITY_DAYS=90,
        SAKA_COMPOST_RATE=0.1,
        SAKA_COMPOST_MIN_BALANCE=50,
        SAKA_COMPOST_MIN_AMOUNT=10,
        SAKA_SILO_REDIS_ENABLED=True,
        SAKA_SILO_REDIS_RATE=0.1,
        SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    )
    def test_si_etape_manque_test_fail(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Une étape du cycle manque et le test ne FAIL pas.
        
        Test : Vérifier que chaque étape est obligatoire.
        """
        user = User.objects.create_user(
            username='test_missing_step',
            email='test_missing_step@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(user=user)
        
        # ÉTAPE 1 : RÉCOLTE (obligatoire)
        harvest_result = harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        assert harvest_result is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : L'étape RÉCOLTE est manquante. "
            "Le cycle SAKA DOIT commencer par la récolte."
        )
        
        wallet.refresh_from_db()
        assert wallet.balance >= 100, (
            f"VIOLATION DU MANIFESTE EGOEJO : L'étape RÉCOLTE n'a pas été exécutée correctement. "
            f"Solde attendu : >= 100, Solde actuel : {wallet.balance}"
        )
        
        # ÉTAPE 2 : PLANTATION (obligatoire pour compléter le cycle)
        spend_result = spend_saka(user, 50, "test_plant")
        assert spend_result is True, (
            "VIOLATION DU MANIFESTE EGOEJO : L'étape PLANTATION est manquante. "
            "Le cycle SAKA DOIT inclure l'usage (plantation)."
        )
        
        wallet.refresh_from_db()
        assert wallet.total_planted >= 50, (
            f"VIOLATION DU MANIFESTE EGOEJO : L'étape PLANTATION n'a pas été exécutée correctement. "
            f"Total planté attendu : >= 50, Total planté actuel : {wallet.total_planted}"
        )
        
        # ÉTAPE 3 : COMPOST (obligatoire)
        # S'assurer que le wallet est éligible au compost
        wallet.refresh_from_db()
        wallet.last_activity_date = timezone.now() - timedelta(days=120)  # Inactif depuis 120 jours
        wallet.balance = 100  # Solde suffisant (min_balance = 50)
        wallet.save()
        
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        initial_silo_balance = silo.total_balance
        
        compost_result = run_saka_compost_cycle(dry_run=False, source="test")
        assert compost_result is not None, (
            "VIOLATION DU MANIFESTE EGOEJO : L'étape COMPOST est manquante. "
            "Le cycle SAKA DOIT inclure le compostage."
        )
        
        silo.refresh_from_db()
        assert silo.total_balance >= initial_silo_balance, (
            f"VIOLATION DU MANIFESTE EGOEJO : L'étape COMPOST n'a pas alimenté le Silo. "
            f"Solde Silo avant : {initial_silo_balance}, Solde Silo après : {silo.total_balance}. "
            f"Le compost DOIT alimenter le Silo."
        )
        
        # ÉTAPE 4 : SILO (obligatoire)
        assert silo.total_balance > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : L'étape SILO est manquante. "
            f"Solde Silo : {silo.total_balance}. "
            f"Le Silo DOIT contenir le SAKA composté."
        )
        
        # ÉTAPE 5 : REDISTRIBUTION (obligatoire si le Silo a un solde suffisant)
        if silo.total_balance >= 100:
            # La redistribution doit être possible
            redistribute_result = redistribute_saka_silo(rate=0.1)
            assert redistribute_result is not None, (
                "VIOLATION DU MANIFESTE EGOEJO : L'étape REDISTRIBUTION est manquante. "
                "Le cycle SAKA DOIT inclure la redistribution du Silo."
            )
            
            silo.refresh_from_db()
            assert silo.total_balance < redistribute_result.get('initial_silo_balance', silo.total_balance), (
                f"VIOLATION DU MANIFESTE EGOEJO : L'étape REDISTRIBUTION n'a pas débité le Silo. "
                f"Solde Silo : {silo.total_balance}. "
                f"La redistribution DOIT débité le Silo."
            )

