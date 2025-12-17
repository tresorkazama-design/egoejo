# Tests d'intégration Celery pour run_saka_silo_redistribution
"""
Tests d'intégration Celery pour la redistribution du Silo SAKA
Vérifie que la tâche Celery `run_saka_silo_redistribution` fonctionne correctement
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models.saka import SakaWallet, SakaSilo, SakaTransaction
from core.tasks import run_saka_silo_redistribution

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    SAKA_SILO_REDIS_ENABLED=True,
    SAKA_SILO_REDIS_RATE=0.1,  # 10% du Silo
    SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    # Configuration Celery pour tests (mode eager)
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class SakaSiloRedistributionCeleryTestCase(TestCase):
    """
    Tests d'intégration pour la tâche Celery de redistribution du Silo SAKA.
    """
    
    def setUp(self):
        """Prépare les données de test"""
        # Créer des utilisateurs avec wallets éligibles
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        # Créer les wallets SAKA avec activité (total_harvested >= 1)
        self.wallet1, _ = SakaWallet.objects.get_or_create(
            user=self.user1,
            defaults={
                'balance': 50,
                'total_harvested': 100,  # Éligible
                'total_planted': 0,
                'total_composted': 0,
            }
        )
        self.wallet1.balance = 50
        self.wallet1.total_harvested = 100
        self.wallet1.save()
        
        self.wallet2, _ = SakaWallet.objects.get_or_create(
            user=self.user2,
            defaults={
                'balance': 30,
                'total_harvested': 50,  # Éligible
                'total_planted': 0,
                'total_composted': 0,
            }
        )
        self.wallet2.balance = 30
        self.wallet2.total_harvested = 50
        self.wallet2.save()
        
        self.wallet3, _ = SakaWallet.objects.get_or_create(
            user=self.user3,
            defaults={
                'balance': 20,
                'total_harvested': 0,  # NON éligible (total_harvested < 1)
                'total_planted': 0,
                'total_composted': 0,
            }
        )
        self.wallet3.balance = 20
        self.wallet3.total_harvested = 0
        self.wallet3.save()
        
        # Créer ou récupérer le Silo Commun avec un solde
        self.silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 1000,
                'total_composted': 1000,
                'total_cycles': 0,
            }
        )
        self.silo.total_balance = 1000
        self.silo.save()
    
    def test_run_saka_silo_redistribution_task_redistribue_aux_eligibles(self):
        """
        Test que la tâche Celery redistribue correctement le Silo aux wallets éligibles.
        """
        # Soldes initiaux
        silo_balance_initial = self.silo.total_balance  # 1000
        wallet1_balance_initial = self.wallet1.balance  # 50
        wallet2_balance_initial = self.wallet2.balance  # 30
        wallet3_balance_initial = self.wallet3.balance  # 20
        
        # Calculer le montant attendu
        # 1000 * 0.1 = 100 grains à redistribuer
        # 2 wallets éligibles (user1 et user2)
        # 100 / 2 = 50 grains par wallet
        expected_redistributed = int(1000 * 0.1)  # 100 grains
        expected_per_wallet = expected_redistributed // 2  # 50 grains
        expected_silo_after = silo_balance_initial - expected_redistributed  # 900
        
        # Appeler la tâche Celery (en mode eager, elle s'exécute immédiatement)
        result = run_saka_silo_redistribution.apply()
        
        # Vérifier que la tâche s'est exécutée avec succès
        self.assertTrue(result.successful())
        result_data = result.result
        
        # Vérifier la structure de la réponse
        self.assertIn('ok', result_data)
        self.assertTrue(result_data['ok'], "La redistribution doit avoir réussi")
        self.assertIn('redistributed', result_data)
        self.assertIn('eligible_wallets', result_data)
        self.assertIn('per_wallet', result_data)
        
        # Recharger les wallets depuis la DB
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.wallet3.refresh_from_db()
        self.silo.refresh_from_db()
        
        # Assertions : Wallets éligibles
        # Wallet1 doit avoir reçu 50 grains
        self.assertEqual(
            self.wallet1.balance,
            wallet1_balance_initial + expected_per_wallet,
            f"Le wallet1 doit avoir reçu {expected_per_wallet} grains"
        )
        self.assertEqual(
            self.wallet1.total_harvested,
            100 + expected_per_wallet,  # total_harvested est incrémenté
            "Le total_harvested du wallet1 doit être incrémenté"
        )
        
        # Wallet2 doit avoir reçu 50 grains
        self.assertEqual(
            self.wallet2.balance,
            wallet2_balance_initial + expected_per_wallet,
            f"Le wallet2 doit avoir reçu {expected_per_wallet} grains"
        )
        self.assertEqual(
            self.wallet2.total_harvested,
            50 + expected_per_wallet,
            "Le total_harvested du wallet2 doit être incrémenté"
        )
        
        # Assertions : Wallet non éligible
        # Wallet3 ne doit PAS avoir reçu de grains
        self.assertEqual(
            self.wallet3.balance,
            wallet3_balance_initial,
            "Le wallet3 (non éligible) ne doit pas avoir reçu de grains"
        )
        self.assertEqual(
            self.wallet3.total_harvested,
            0,
            "Le total_harvested du wallet3 ne doit pas avoir changé"
        )
        
        # Assertions : Silo Commun
        # Le silo doit avoir diminué
        self.assertEqual(
            self.silo.total_balance,
            expected_silo_after,
            f"Le Silo doit avoir diminué de {expected_redistributed} grains"
        )
        
        # Assertions : Résultat de la tâche
        self.assertEqual(result_data['eligible_wallets'], 2, "2 wallets doivent être éligibles")
        self.assertEqual(result_data['redistributed'], expected_redistributed, "Le total redistribué doit être correct")
        self.assertEqual(result_data['per_wallet'], expected_per_wallet, "Le montant par wallet doit être correct")
        self.assertEqual(result_data['total_before'], silo_balance_initial, "Le solde initial du Silo doit être correct")
        self.assertEqual(result_data['total_after'], expected_silo_after, "Le solde final du Silo doit être correct")
        
        # Assertions : SakaTransaction
        # Des transactions EARN doivent avoir été créées pour les wallets éligibles
        transactions1 = SakaTransaction.objects.filter(
            user=self.user1,
            direction='EARN',
            reason='silo_redistribution',
        )
        self.assertEqual(transactions1.count(), 1, "Une transaction doit avoir été créée pour user1")
        self.assertEqual(transactions1.first().amount, expected_per_wallet, "La transaction doit avoir le bon montant")
        
        transactions2 = SakaTransaction.objects.filter(
            user=self.user2,
            direction='EARN',
            reason='silo_redistribution',
        )
        self.assertEqual(transactions2.count(), 1, "Une transaction doit avoir été créée pour user2")
        self.assertEqual(transactions2.first().amount, expected_per_wallet, "La transaction doit avoir le bon montant")
        
        # Aucune transaction pour user3
        transactions3 = SakaTransaction.objects.filter(
            user=self.user3,
            direction='EARN',
            reason='silo_redistribution',
        )
        self.assertEqual(transactions3.count(), 0, "Aucune transaction ne doit avoir été créée pour user3")
    
    def test_run_saka_silo_redistribution_task_ne_fait_rien_si_desactive(self):
        """
        Test que la tâche Celery ne fait rien si la redistribution est désactivée.
        """
        # Désactiver la redistribution pour ce test
        with override_settings(SAKA_SILO_REDIS_ENABLED=False):
            # Soldes initiaux
            silo_balance_initial = self.silo.total_balance
            wallet1_balance_initial = self.wallet1.balance
            
            # Appeler la tâche Celery
            result = run_saka_silo_redistribution.apply()
            
            # Vérifier que la tâche s'est exécutée avec succès
            self.assertTrue(result.successful())
            result_data = result.result
            
            # Vérifier que la redistribution n'a pas été effectuée
            self.assertFalse(result_data.get('ok', True), "La redistribution doit être désactivée")
            self.assertEqual(result_data.get('reason'), 'disabled', "La raison doit être 'disabled'")
            
            # Recharger les wallets depuis la DB
            self.wallet1.refresh_from_db()
            self.silo.refresh_from_db()
            
            # Assertions : Rien ne doit avoir changé
            self.assertEqual(
                self.wallet1.balance,
                wallet1_balance_initial,
                "Le wallet ne doit pas avoir changé"
            )
            self.assertEqual(
                self.silo.total_balance,
                silo_balance_initial,
                "Le Silo ne doit pas avoir changé"
            )
    
    def test_run_saka_silo_redistribution_task_ne_fait_rien_si_silo_vide(self):
        """
        Test que la tâche Celery ne fait rien si le Silo est vide.
        """
        # Vider le Silo
        self.silo.total_balance = 0
        self.silo.save()
        
        # Soldes initiaux
        wallet1_balance_initial = self.wallet1.balance
        
        # Appeler la tâche Celery
        result = run_saka_silo_redistribution.apply()
        
        # Vérifier que la tâche s'est exécutée avec succès
        self.assertTrue(result.successful())
        result_data = result.result
        
        # Vérifier que la redistribution n'a pas été effectuée
        self.assertFalse(result_data.get('ok', True), "La redistribution ne doit pas avoir été effectuée")
        self.assertIn('reason', result_data)
        
        # Recharger le wallet depuis la DB
        self.wallet1.refresh_from_db()
        
        # Assertions : Rien ne doit avoir changé
        self.assertEqual(
            self.wallet1.balance,
            wallet1_balance_initial,
            "Le wallet ne doit pas avoir changé"
        )

