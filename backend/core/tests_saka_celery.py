# Tests d'intégration Celery pour run_saka_compost_cycle
"""
Tests d'intégration Celery pour le compostage SAKA
Vérifie que la tâche Celery `saka_run_compost_cycle` fonctionne correctement
"""
import os
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models.saka import SakaWallet, SakaCompostLog, SakaSilo, SakaCycle, SakaTransaction
from core.tasks import saka_run_compost_cycle

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    SAKA_COMPOST_ENABLED=True,
    SAKA_COMPOST_INACTIVITY_DAYS=90,
    SAKA_COMPOST_RATE=0.1,  # 10% du solde
    SAKA_COMPOST_MIN_BALANCE=50,
    SAKA_COMPOST_MIN_AMOUNT=10,
    # Configuration Celery pour tests (mode eager)
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class SakaCompostCeleryTestCase(TestCase):
    """
    Tests d'intégration pour la tâche Celery de compostage SAKA.
    """
    
    def setUp(self):
        """Prépare les données de test"""
        # Créer deux utilisateurs
        self.user_actif = User.objects.create_user(
            username='user_actif',
            email='actif@test.com',
            password='testpass123'
        )
        self.user_inactif = User.objects.create_user(
            username='user_inactif',
            email='inactif@test.com',
            password='testpass123'
        )
        
        # Créer les wallets SAKA
        # User actif : activité récente (il y a 30 jours)
        self.wallet_actif, _ = SakaWallet.objects.get_or_create(
            user=self.user_actif,
            defaults={
                'balance': 200,
                'total_harvested': 200,
                'total_planted': 0,
                'total_composted': 0,
                'last_activity_date': timezone.now() - timedelta(days=30),  # Actif récemment
            }
        )
        # S'assurer que le wallet existe avec les bonnes valeurs
        self.wallet_actif.balance = 200
        self.wallet_actif.last_activity_date = timezone.now() - timedelta(days=30)
        self.wallet_actif.save()
        
        # User inactif : aucune activité depuis plus de 90 jours
        self.wallet_inactif, _ = SakaWallet.objects.get_or_create(
            user=self.user_inactif,
            defaults={
                'balance': 150,
                'total_harvested': 150,
                'total_planted': 0,
                'total_composted': 0,
                'last_activity_date': timezone.now() - timedelta(days=120),  # Inactif depuis 120 jours
            }
        )
        # S'assurer que le wallet existe avec les bonnes valeurs
        self.wallet_inactif.balance = 150
        self.wallet_inactif.last_activity_date = timezone.now() - timedelta(days=120)
        self.wallet_inactif.save()
        
        # Créer ou récupérer le Silo Commun
        self.silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        
        # Compter les logs de compost existants
        self.initial_compost_logs_count = SakaCompostLog.objects.count()
    
    def test_compost_cycle_moves_inactive_saka_to_silo(self):
        """
        Test que le compostage déplace les SAKA inactifs vers le Silo.
        Créer 2 users avec SakaWallet :
        - user_actif : balance 100, last_activity_date récente.
        - user_inactif : balance 150, last_activity_date ancienne (> seuil compost).
        Appeler directement le service run_saka_compost_cycle() (sans Celery pour ce test).
        Assert :
        - Le wallet du user_inactif a diminué (ou mis à 0 selon ta règle).
        - Le wallet du user_actif n'a pas bougé.
        - SakaSilo.total_balance a augmenté de la somme compostée.
        - Un SakaCompostLog a été créé avec les bons agrégats (total_composted, nb_wallets).
        """
        # Solde initial
        balance_actif_initial = self.wallet_actif.balance  # 200
        balance_inactif_initial = self.wallet_inactif.balance  # 150
        silo_balance_initial = self.silo.total_balance
        
        # Calculer le montant attendu pour le wallet inactif
        # 150 * 0.1 = 15 grains compostés
        expected_composted = int(150 * 0.1)  # 15 grains
        expected_balance_after = balance_inactif_initial - expected_composted  # 150 - 15 = 135
        
        # Appeler la tâche Celery (en mode eager, elle s'exécute immédiatement)
        # Note: avec bind=True, la tâche reçoit self comme premier argument
        result = saka_run_compost_cycle.apply(kwargs={'dry_run': False})
        
        # Vérifier que la tâche s'est exécutée avec succès
        self.assertTrue(result.successful())
        result_data = result.result
        
        # Vérifier la structure de la réponse
        self.assertIn('wallets_affected', result_data)
        self.assertIn('total_composted', result_data)
        self.assertIn('cycles', result_data)
        
        # Recharger les wallets depuis la DB
        self.wallet_actif.refresh_from_db()
        self.wallet_inactif.refresh_from_db()
        self.silo.refresh_from_db()
        
        # Assertions : User actif
        # Son solde ne doit PAS avoir changé (activité récente)
        self.assertEqual(
            self.wallet_actif.balance,
            balance_actif_initial,
            "Le wallet actif ne doit pas être composté"
        )
        self.assertEqual(
            self.wallet_actif.total_composted,
            0,
            "Le wallet actif ne doit pas avoir de compostage"
        )
        
        # Assertions : User inactif
        # Son solde doit avoir diminué
        self.assertEqual(
            self.wallet_inactif.balance,
            expected_balance_after,
            f"Le wallet inactif doit avoir été composté de {expected_composted} grains"
        )
        self.assertEqual(
            self.wallet_inactif.total_composted,
            expected_composted,
            f"Le total_composted du wallet inactif doit être {expected_composted}"
        )
        # La date d'activité doit avoir été réinitialisée
        self.assertIsNotNone(self.wallet_inactif.last_activity_date)
        self.assertAlmostEqual(
            self.wallet_inactif.last_activity_date,
            timezone.now(),
            delta=timedelta(seconds=5),
            msg="La date d'activité doit avoir été réinitialisée"
        )
        
        # Assertions : Silo Commun
        # Le silo doit avoir reçu les grains compostés
        self.assertEqual(
            self.silo.total_balance,
            silo_balance_initial + expected_composted,
            f"Le Silo doit avoir reçu {expected_composted} grains"
        )
        self.assertEqual(
            self.silo.total_composted,
            silo_balance_initial + expected_composted,
            "Le total_composted du Silo doit être mis à jour"
        )
        self.assertEqual(
            self.silo.total_cycles,
            1,
            "Le nombre de cycles doit être incrémenté"
        )
        self.assertIsNotNone(self.silo.last_compost_at)
        
        # Assertions : Résultat de la tâche
        self.assertEqual(result_data['wallets_affected'], 1, "Un seul wallet doit être affecté")
        self.assertEqual(result_data['total_composted'], expected_composted, "Le total composté doit être correct")
        self.assertEqual(result_data['cycles'], 1, "Un cycle doit avoir été exécuté")
        
        # Assertions : SakaCompostLog
        # Un nouveau log doit avoir été créé
        new_logs = SakaCompostLog.objects.filter(id__gt=self.initial_compost_logs_count)
        self.assertEqual(new_logs.count(), 1, "Un seul log de compost doit avoir été créé")
        
        log = new_logs.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.wallets_affected, 1, "Le log doit indiquer 1 wallet affecté")
        self.assertEqual(log.total_composted, expected_composted, "Le log doit indiquer le bon montant composté")
        self.assertFalse(log.dry_run, "Le log ne doit pas être en mode dry_run")
        self.assertEqual(log.source, "celery", "Le log doit indiquer 'celery' comme source")
        self.assertIsNotNone(log.finished_at, "Le log doit avoir une date de fin")
        
        # Assertions : SakaTransaction
        # Une transaction SPEND doit avoir été créée pour le wallet inactif
        compost_transactions = SakaTransaction.objects.filter(
            user=self.user_inactif,
            direction='SPEND',
            reason='compost',
        )
        self.assertEqual(compost_transactions.count(), 1, "Une transaction de compost doit avoir été créée")
        
        transaction = compost_transactions.first()
        self.assertEqual(transaction.amount, expected_composted, "La transaction doit avoir le bon montant")
        self.assertIn('source', transaction.metadata, "La transaction doit avoir des métadonnées")
        self.assertEqual(transaction.metadata['source'], 'compost_cycle', "La source doit être 'compost_cycle'")
    
    def test_saka_compost_cycle_task_ne_fait_rien_si_pas_d_eligibles(self):
        """
        Test que la tâche Celery ne fait rien s'il n'y a pas de wallets éligibles.
        """
        # Modifier les wallets pour qu'aucun ne soit éligible
        # Option 1 : User actif reste actif (déjà fait dans setUp)
        # Option 2 : User inactif devient actif
        self.wallet_inactif.last_activity_date = timezone.now() - timedelta(days=30)  # Actif récemment
        self.wallet_inactif.save()
        
        # Solde initial
        balance_actif_initial = self.wallet_actif.balance
        balance_inactif_initial = self.wallet_inactif.balance
        silo_balance_initial = self.silo.total_balance
        silo_cycles_initial = self.silo.total_cycles
        
        # Compter les logs existants
        initial_logs_count = SakaCompostLog.objects.count()
        
        # Appeler la tâche Celery
        result = saka_run_compost_cycle.apply(kwargs={'dry_run': False})
        
        # Vérifier que la tâche s'est exécutée avec succès
        self.assertTrue(result.successful())
        result_data = result.result
        
        # Recharger les wallets depuis la DB
        self.wallet_actif.refresh_from_db()
        self.wallet_inactif.refresh_from_db()
        self.silo.refresh_from_db()
        
        # Assertions : Aucun wallet ne doit avoir changé
        self.assertEqual(
            self.wallet_actif.balance,
            balance_actif_initial,
            "Le wallet actif ne doit pas avoir changé"
        )
        self.assertEqual(
            self.wallet_inactif.balance,
            balance_inactif_initial,
            "Le wallet inactif (maintenant actif) ne doit pas avoir changé"
        )
        
        # Assertions : Le Silo ne doit pas avoir changé
        self.assertEqual(
            self.silo.total_balance,
            silo_balance_initial,
            "Le Silo ne doit pas avoir changé"
        )
        self.assertEqual(
            self.silo.total_cycles,
            silo_cycles_initial,
            "Le nombre de cycles ne doit pas avoir changé"
        )
        
        # Assertions : Résultat de la tâche
        self.assertEqual(result_data['wallets_affected'], 0, "Aucun wallet ne doit être affecté")
        self.assertEqual(result_data['total_composted'], 0, "Aucun grain ne doit être composté")
        self.assertEqual(result_data['cycles'], 0, "Aucun cycle ne doit avoir été exécuté")
        
        # Assertions : Un log doit quand même avoir été créé (pour audit)
        new_logs = SakaCompostLog.objects.filter(id__gt=initial_logs_count)
        self.assertEqual(new_logs.count(), 1, "Un log doit avoir été créé même si aucun wallet n'est éligible")
        
        log = new_logs.first()
        self.assertEqual(log.wallets_affected, 0, "Le log doit indiquer 0 wallet affecté")
        self.assertEqual(log.total_composted, 0, "Le log doit indiquer 0 grain composté")
        self.assertIsNotNone(log.finished_at, "Le log doit avoir une date de fin")
        
        # Assertions : Aucune transaction ne doit avoir été créée
        new_transactions = SakaTransaction.objects.filter(
            user__in=[self.user_actif, self.user_inactif],
            direction='SPEND',
            reason='compost',
            created_at__gte=timezone.now() - timedelta(minutes=1)
        )
        self.assertEqual(new_transactions.count(), 0, "Aucune transaction de compost ne doit avoir été créée")
    
    def test_saka_compost_cycle_task_avec_saka_cycle_actif(self):
        """
        Test que la tâche Celery associe correctement le log au SakaCycle actif.
        """
        # Créer un cycle SAKA actif
        active_cycle = SakaCycle.objects.create(
            name='Cycle Test 2025',
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True,
        )
        
        # Appeler la tâche Celery
        result = saka_run_compost_cycle.apply(kwargs={'dry_run': False})
        
        # Vérifier que la tâche s'est exécutée avec succès
        self.assertTrue(result.successful())
        
        # Vérifier que le log est associé au cycle
        new_logs = SakaCompostLog.objects.filter(id__gt=self.initial_compost_logs_count)
        self.assertEqual(new_logs.count(), 1, "Un log doit avoir été créé")
        
        log = new_logs.first()
        self.assertEqual(log.cycle, active_cycle, "Le log doit être associé au cycle actif")
    
    def test_saka_compost_cycle_task_respecte_min_balance(self):
        """
        Test que la tâche ne composte pas les wallets avec un solde inférieur au minimum.
        """
        # Créer un wallet inactif avec un solde trop faible
        user_trop_faible = User.objects.create_user(
            username='user_trop_faible',
            email='faible@test.com',
            password='testpass123'
        )
        wallet_trop_faible, _ = SakaWallet.objects.get_or_create(
            user=user_trop_faible,
            defaults={
                'balance': 30,  # < 50 (min_balance)
                'total_harvested': 30,
                'last_activity_date': timezone.now() - timedelta(days=120),  # Inactif
            }
        )
        wallet_trop_faible.balance = 30
        wallet_trop_faible.last_activity_date = timezone.now() - timedelta(days=120)
        wallet_trop_faible.save()
        
        # S'assurer que le wallet inactif principal a un solde suffisant
        self.wallet_inactif.balance = 150
        self.wallet_inactif.save()
        
        balance_trop_faible_initial = wallet_trop_faible.balance
        
        # Appeler la tâche Celery
        result = saka_run_compost_cycle.apply(kwargs={'dry_run': False})
        
        # Vérifier que la tâche s'est exécutée avec succès
        self.assertTrue(result.successful())
        
        # Recharger le wallet
        wallet_trop_faible.refresh_from_db()
        
        # Assertions : Le wallet avec solde trop faible ne doit pas avoir été composté
        self.assertEqual(
            wallet_trop_faible.balance,
            balance_trop_faible_initial,
            "Le wallet avec solde trop faible ne doit pas être composté"
        )
        
        # Mais le wallet inactif avec solde suffisant doit avoir été composté
        self.wallet_inactif.refresh_from_db()
        self.assertLess(
            self.wallet_inactif.balance,
            150,
            "Le wallet inactif avec solde suffisant doit avoir été composté"
        )
    
    def test_compost_cycle_is_idempotent_for_same_cycle(self):
        """
        Test que le compostage est idempotent : le même SAKA n'est pas composté deux fois.
        Le Silo ne double pas le montant.
        """
        from core.services.saka import run_saka_compost_cycle
        
        # Solde initial
        balance_inactif_initial = self.wallet_inactif.balance  # 150
        silo_balance_initial = self.silo.total_balance
        
        # Calculer le montant attendu pour le premier compostage
        # 150 * 0.1 = 15 grains compostés
        expected_composted_first = int(150 * 0.1)  # 15 grains
        
        # Premier appel du service (sans passer par Celery pour ce test)
        result1 = run_saka_compost_cycle(dry_run=False, source="test")
        
        # Vérifier que le premier compostage a fonctionné
        self.assertEqual(result1['wallets_affected'], 1)
        self.assertEqual(result1['total_composted'], expected_composted_first)
        
        # Recharger les données
        self.wallet_inactif.refresh_from_db()
        self.silo.refresh_from_db()
        
        # Vérifier que le wallet a été composté
        balance_after_first = self.wallet_inactif.balance
        silo_balance_after_first = self.silo.total_balance
        
        self.assertEqual(balance_after_first, balance_inactif_initial - expected_composted_first)
        self.assertEqual(silo_balance_after_first, silo_balance_initial + expected_composted_first)
        
        # IMPORTANT : Le wallet a maintenant une date d'activité récente (réinitialisée)
        # donc il ne sera plus éligible pour le compostage immédiatement
        self.assertIsNotNone(self.wallet_inactif.last_activity_date)
        self.assertAlmostEqual(
            self.wallet_inactif.last_activity_date,
            timezone.now(),
            delta=timedelta(seconds=5)
        )
        
        # Deuxième appel du service (devrait ne rien faire car le wallet est maintenant "actif")
        result2 = run_saka_compost_cycle(dry_run=False, source="test")
        
        # Vérifier que le deuxième appel n'a rien composté
        self.assertEqual(result2['wallets_affected'], 0)
        self.assertEqual(result2['total_composted'], 0)
        
        # Recharger les données
        self.wallet_inactif.refresh_from_db()
        self.silo.refresh_from_db()
        
        # Vérifier que rien n'a changé
        self.assertEqual(self.wallet_inactif.balance, balance_after_first)
        self.assertEqual(self.silo.total_balance, silo_balance_after_first)
        
        # Vérifier que le Silo n'a pas doublé
        self.assertEqual(
            self.silo.total_balance,
            silo_balance_initial + expected_composted_first,
            "Le Silo ne doit pas avoir doublé le montant"
        )
        
        # Vérifier les logs : deux logs doivent avoir été créés
        logs = SakaCompostLog.objects.filter(id__gt=self.initial_compost_logs_count).order_by('started_at')
        self.assertEqual(logs.count(), 2, "Deux logs doivent avoir été créés")
        
        log1 = logs[0]
        log2 = logs[1]
        
        self.assertEqual(log1.total_composted, expected_composted_first)
        self.assertEqual(log2.total_composted, 0)
    
    def test_celery_task_triggers_compost_service(self):
        """
        Test que la tâche Celery appelle bien le service run_saka_compost_cycle.
        """
        from unittest.mock import patch
        
        # Mock du service (le chemin doit correspondre à l'import dans tasks.py)
        mock_result = {
            "cycles": 1,
            "wallets_affected": 1,
            "total_composted": 15,
            "dry_run": False,
            "log_id": 999
        }
        
        # Patcher le service au niveau de l'import dans tasks.py
        with patch('core.services.saka.run_saka_compost_cycle', return_value=mock_result) as mock_service:
            # Appeler la tâche Celery
            result = saka_run_compost_cycle.apply(kwargs={'dry_run': False})
            
            # Vérifier que la tâche s'est exécutée avec succès
            self.assertTrue(result.successful())
            
            # Vérifier que le service a été appelé une fois avec les bons paramètres
            self.assertEqual(mock_service.call_count, 1)
            mock_service.assert_called_once_with(dry_run=False, source="celery")
            
            # Vérifier que le résultat de la tâche correspond au mock
            self.assertEqual(result.result, mock_result)

