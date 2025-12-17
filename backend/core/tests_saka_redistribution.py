"""
Tests pour la redistribution du Silo Commun SAKA.
Vérifie que la redistribution fonctionne correctement et que personne ne peut aller en balance négative.
"""
import json
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.db.models import F
from core.models.saka import SakaCycle, SakaSilo, SakaTransaction, SakaCompostLog, SakaWallet
from django.utils import timezone
from datetime import date, timedelta, datetime

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    SAKA_SILO_REDIS_ENABLED=True,
    SAKA_SILO_REDIS_RATE=0.1,
    SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1
)
class SakaRedistributionTestCase(TestCase):
    """Tests pour la redistribution du Silo Commun SAKA"""
    
    def setUp(self):
        self.client = TestCase.client_class()
        
        # Créer des utilisateurs et leurs wallets
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123'
        )
        self.user4 = User.objects.create_user(
            username='user4',
            email='user4@example.com',
            password='testpass123'
        )
        
        # Créer des wallets avec différentes configurations
        self.wallet1, _ = SakaWallet.objects.get_or_create(
            user=self.user1,
            defaults={
                'balance': 100,
                'total_harvested': 200,
                'total_planted': 100,
            }
        )
        # Mettre à jour si le wallet existait déjà
        self.wallet1.balance = 100
        self.wallet1.total_harvested = 200
        self.wallet1.total_planted = 100
        self.wallet1.save()
        
        self.wallet2, _ = SakaWallet.objects.get_or_create(
            user=self.user2,
            defaults={
                'balance': 50,
                'total_harvested': 150,
                'total_planted': 100,
            }
        )
        self.wallet2.balance = 50
        self.wallet2.total_harvested = 150
        self.wallet2.total_planted = 100
        self.wallet2.save()
        
        self.wallet3, _ = SakaWallet.objects.get_or_create(
            user=self.user3,
            defaults={
                'balance': 0,  # Balance à 0 mais total_harvested > 0 (actif)
                'total_harvested': 50,
                'total_planted': 50,
            }
        )
        self.wallet3.balance = 0
        self.wallet3.total_harvested = 50
        self.wallet3.total_planted = 50
        self.wallet3.save()
        
        self.wallet4, _ = SakaWallet.objects.get_or_create(
            user=self.user4,
            defaults={
                'balance': 0,  # Inactif (balance=0 et total_harvested=0)
                'total_harvested': 0,
                'total_planted': 0,
            }
        )
        self.wallet4.balance = 0
        self.wallet4.total_harvested = 0
        self.wallet4.total_planted = 0
        self.wallet4.save()
        
        # Créer le Silo commun avec un montant
        SakaSilo.objects.filter(id=1).delete()
        self.silo = SakaSilo.objects.create(
            id=1,
            total_balance=1000,
            total_composted=1000,
            total_cycles=1,
        )
    
    def test_redistribute_silo_empty(self):
        """Test que la redistribution ne fait rien si le Silo est vide"""
        from core.services.saka import redistribute_saka_silo
        
        # Vider le Silo
        self.silo.total_balance = 0
        self.silo.save()
        
        result = redistribute_saka_silo()
        
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "nothing_to_redistribute")
        self.assertEqual(result["total_before"], 0)
        
        # Vérifier que les balances n'ont pas changé
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.wallet3.refresh_from_db()
        self.assertEqual(self.wallet1.balance, 100)
        self.assertEqual(self.wallet2.balance, 50)
        self.assertEqual(self.wallet3.balance, 0)
    
    def test_redistribute_silo_with_active_wallets(self):
        """Test la redistribution avec 4 wallets actifs (3 avec balance>0 ou total_harvested>0)"""
        from core.services.saka import redistribute_saka_silo
        
        # Silo avec 1000 grains, rate=0.1 (10%) = 100 grains à redistribuer
        # 3 wallets actifs (user1, user2, user3) → 100 / 3 = 33 grains chacun
        result = redistribute_saka_silo(rate=0.1)
        
        self.assertTrue(result["ok"])
        self.assertEqual(result["redistributed"], 99)  # 33 * 3 = 99 (floor)
        self.assertEqual(result["eligible_wallets"], 3)  # user1, user2, user3 (pas user4)
        self.assertEqual(result["per_wallet"], 33)
        self.assertEqual(result["total_before"], 1000)
        self.assertEqual(result["total_after"], 901)  # 1000 - 99
        
        # Vérifier que les balances ont été mises à jour
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.wallet3.refresh_from_db()
        self.wallet4.refresh_from_db()
        
        self.assertEqual(self.wallet1.balance, 133)  # 100 + 33
        self.assertEqual(self.wallet2.balance, 83)   # 50 + 33
        self.assertEqual(self.wallet3.balance, 33)   # 0 + 33
        self.assertEqual(self.wallet4.balance, 0)    # Inactif, pas de redistribution
        
        # Vérifier que total_harvested a été mis à jour
        self.assertEqual(self.wallet1.total_harvested, 233)  # 200 + 33
        self.assertEqual(self.wallet2.total_harvested, 183)  # 150 + 33
        self.assertEqual(self.wallet3.total_harvested, 83)   # 50 + 33
        
        # Vérifier que le Silo a été mis à jour
        self.silo.refresh_from_db()
        self.assertEqual(self.silo.total_balance, 901)
        
        # Vérifier que les transactions ont été créées
        transactions = SakaTransaction.objects.filter(
            reason='silo_redistribution',
            direction='EARN'
        )
        self.assertEqual(transactions.count(), 3)
        
        # Vérifier les montants des transactions
        for transaction in transactions:
            self.assertEqual(transaction.amount, 33)
            self.assertIn(transaction.user, [self.user1, self.user2, self.user3])
            self.assertEqual(transaction.reason, 'silo_redistribution')
    
    def test_redistribute_silo_no_active_wallets(self):
        """Test que la redistribution ne fait rien s'il n'y a pas de wallets actifs"""
        from core.services.saka import redistribute_saka_silo
        
        # Désactiver tous les wallets
        SakaWallet.objects.all().update(balance=0, total_harvested=0)
        
        result = redistribute_saka_silo(rate=0.1)
        
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "no_eligible_wallets")
        self.assertEqual(result["redistributed"], 0)
        self.assertEqual(result["total_before"], 1000)
        
        # Vérifier que le Silo n'a pas changé
        self.silo.refresh_from_db()
        self.assertEqual(self.silo.total_balance, 1000)
    
    def test_redistribute_silo_custom_rate(self):
        """Test la redistribution avec un taux personnalisé"""
        from core.services.saka import redistribute_saka_silo
        
        # Redistribuer 20% du Silo (200 grains)
        # 3 wallets actifs → 200 / 3 = 66 grains chacun
        result = redistribute_saka_silo(rate=0.2)
        
        self.assertTrue(result["ok"])
        self.assertEqual(result["redistributed"], 198)  # 66 * 3 = 198
        self.assertEqual(result["per_wallet"], 66)
        self.assertEqual(result["total_after"], 802)  # 1000 - 198
    
    def test_redistribute_silo_invalid_rate(self):
        """Test que la redistribution refuse un taux invalide"""
        from core.services.saka import redistribute_saka_silo
        
        # Taux négatif ou nul
        result = redistribute_saka_silo(rate=-0.1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "nothing_to_redistribute")
        
        # Taux = 0
        result = redistribute_saka_silo(rate=0.0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "nothing_to_redistribute")
    
    def test_redistribute_silo_no_negative_balance(self):
        """Test que personne ne peut aller en balance négative"""
        from core.services.saka import redistribute_saka_silo
        
        # Vérifier que les balances initiales sont positives ou nulles
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.wallet3.refresh_from_db()
        
        initial_balance1 = self.wallet1.balance
        initial_balance2 = self.wallet2.balance
        initial_balance3 = self.wallet3.balance
        
        # Redistribuer
        result = redistribute_saka_silo(rate=0.1)
        
        self.assertTrue(result["ok"])
        
        # Vérifier que toutes les balances sont >= 0
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.wallet3.refresh_from_db()
        
        self.assertGreaterEqual(self.wallet1.balance, 0)
        self.assertGreaterEqual(self.wallet2.balance, 0)
        self.assertGreaterEqual(self.wallet3.balance, 0)
        
        # Vérifier que les balances ont augmenté (redistribution = EARN)
        self.assertGreaterEqual(self.wallet1.balance, initial_balance1)
        self.assertGreaterEqual(self.wallet2.balance, initial_balance2)
        self.assertGreaterEqual(self.wallet3.balance, initial_balance3)
    
    def test_redistribute_silo_atomic_transaction(self):
        """Test que la redistribution est atomique (tout ou rien)"""
        from core.services.saka import redistribute_saka_silo
        from django.db import transaction
        
        # Vérifier l'état initial
        initial_silo_balance = self.silo.total_balance
        initial_wallet1_balance = self.wallet1.balance
        
        # Redistribuer
        result = redistribute_saka_silo(rate=0.1)
        
        self.assertTrue(result["ok"])
        
        # Vérifier que soit tout a été mis à jour, soit rien
        self.silo.refresh_from_db()
        self.wallet1.refresh_from_db()
        
        # Si la redistribution a réussi, le Silo et les wallets doivent être cohérents
        if result["redistributed"] > 0:
            self.assertEqual(
                self.silo.total_balance,
                initial_silo_balance - result["redistributed"]
            )
            self.assertEqual(
                self.wallet1.balance,
                initial_wallet1_balance + result["per_wallet"]
            )
    
    def test_api_redistribute_admin_only(self):
        """Test que l'endpoint /api/saka/redistribute/ est accessible uniquement aux admins"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Utilisateur normal
        normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='testpass123'
        )
        self.client.force_login(normal_user)
        
        response = self.client.post('/api/saka/redistribute/')
        self.assertIn(response.status_code, [403, 401])  # Forbidden ou Unauthorized
        
        # Admin
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_login(admin_user)
        
        response = self.client.post('/api/saka/redistribute/', {
            'rate': 0.1
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["ok"])
        self.assertGreater(data["redistributed"], 0)
    
    def test_api_redistribute_with_custom_rate(self):
        """Test l'endpoint avec un taux personnalisé"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_login(admin_user)
        
        # Redistribuer 5% du Silo
        response = self.client.post('/api/saka/redistribute/', {
            'rate': 0.05
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["ok"])
        
        # Vérifier que le montant redistribué correspond à 5% (50 grains)
        # 50 / 3 wallets = 16 grains chacun (floor)
        self.assertEqual(data["redistributed"], 48)  # 16 * 3
        self.assertEqual(data["per_wallet"], 16)

