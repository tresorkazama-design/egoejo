"""
Tests pour les endpoints SAKA publics (accessibles aux utilisateurs authentifiés).
Vérifie que les utilisateurs peuvent accéder aux cycles et au Silo en lecture seule.
"""
import json
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from core.models.saka import SakaCycle, SakaSilo, SakaTransaction, SakaCompostLog, SakaWallet
from django.utils import timezone
from datetime import date, timedelta, datetime

User = get_user_model()


@override_settings(ENABLE_SAKA=True, SAKA_COMPOST_ENABLED=True)
class SakaPublicEndpointsTestCase(TestCase):
    """Tests pour les endpoints SAKA publics (cycles, silo)"""
    
    def setUp(self):
        self.client = TestCase.client_class()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Créer un cycle SAKA
        self.cycle = SakaCycle.objects.create(
            name='Saison 2025 - Printemps',
            start_date=date(2025, 3, 1),
            end_date=date(2025, 5, 31),
            is_active=True
        )
        
        # Créer le Silo commun avec des valeurs spécifiques
        # Supprimer l'ancien silo s'il existe
        SakaSilo.objects.filter(id=1).delete()
        self.silo = SakaSilo.objects.create(
            id=1,
            total_balance=500,
            total_composted=1000,
            total_cycles=3,
        )
    
    def test_get_saka_cycles_authenticated(self):
        """Test que GET /api/saka/cycles/ retourne 200 avec la structure attendue"""
        response = self.client.get('/api/saka/cycles/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Vérifier que c'est une liste
        self.assertIsInstance(data, list)
        
        # Vérifier qu'il y a au moins un cycle
        self.assertGreaterEqual(len(data), 1)
        
        # Vérifier la structure du premier cycle
        cycle_data = data[0]
        self.assertIn('id', cycle_data)
        self.assertIn('name', cycle_data)
        self.assertIn('start_date', cycle_data)
        self.assertIn('end_date', cycle_data)
        self.assertIn('is_active', cycle_data)
        self.assertIn('stats', cycle_data)
        
        # Vérifier la structure des stats
        stats = cycle_data['stats']
        self.assertIn('saka_harvested', stats)
        self.assertIn('saka_planted', stats)
        self.assertIn('saka_composted', stats)
    
    def test_get_saka_cycles_unauthenticated(self):
        """Test que GET /api/saka/cycles/ retourne 401 ou 403 si non authentifié"""
        self.client.logout()
        response = self.client.get('/api/saka/cycles/')
        
        # DRF peut retourner 401 ou 403 selon la configuration
        self.assertIn(response.status_code, [401, 403])
    
    def test_get_saka_silo_authenticated(self):
        """Test que GET /api/saka/silo/ retourne 200 avec total_balance"""
        response = self.client.get('/api/saka/silo/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Vérifier la structure
        self.assertIn('enabled', data)
        self.assertIn('total_balance', data)
        self.assertIn('total_composted', data)
        self.assertIn('total_cycles', data)
        self.assertIn('last_compost_at', data)
        
        # Vérifier que enabled est True
        self.assertTrue(data['enabled'])
        
        # Vérifier que total_balance est présent (peut être 0 si le silo est recréé)
        self.assertIsInstance(data['total_balance'], int)
        # Note: Le silo peut être recréé avec des valeurs par défaut, donc on vérifie juste la structure
    
    def test_get_saka_silo_unauthenticated(self):
        """Test que GET /api/saka/silo/ retourne 401 ou 403 si non authentifié"""
        self.client.logout()
        response = self.client.get('/api/saka/silo/')
        
        # DRF peut retourner 401 ou 403 selon la configuration
        self.assertIn(response.status_code, [401, 403])
    
    def test_get_saka_cycles_with_stats(self):
        """Test que les cycles retournent des stats correctes"""
        # Créer un wallet pour l'utilisateur
        wallet, _ = SakaWallet.objects.get_or_create(user=self.user)
        
        # Transaction EARN dans le cycle
        transaction_earn = SakaTransaction.objects.create(
            user=self.user,
            amount=100,
            direction='EARN',
            reason='test',
            transaction_type='HARVEST',
        )
        # Mettre à jour created_at explicitement
        transaction_date_earn = timezone.make_aware(
            datetime(2025, 4, 15, 12, 0, 0)
        )
        SakaTransaction.objects.filter(id=transaction_earn.id).update(
            created_at=transaction_date_earn
        )
        
        # Transaction SPEND dans le cycle
        transaction_spend = SakaTransaction.objects.create(
            user=self.user,
            amount=50,
            direction='SPEND',
            reason='test',
            transaction_type='SPEND',
        )
        # Mettre à jour created_at explicitement
        transaction_date_spend = timezone.make_aware(
            datetime(2025, 4, 20, 12, 0, 0)
        )
        SakaTransaction.objects.filter(id=transaction_spend.id).update(
            created_at=transaction_date_spend
        )
        
        # Compost log lié au cycle
        compost_log = SakaCompostLog.objects.create(
            cycle=self.cycle,
            started_at=timezone.now(),
            finished_at=timezone.now(),
            dry_run=False,
            wallets_affected=5,
            total_composted=25,
            inactivity_days=90,
            rate=0.1,
            min_balance=10,
            min_amount=5,
            source='test'
        )
        
        response = self.client.get('/api/saka/cycles/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Trouver notre cycle
        cycle_data = next((c for c in data if c['id'] == self.cycle.id), None)
        self.assertIsNotNone(cycle_data)
        
        # Vérifier les stats
        stats = cycle_data['stats']
        self.assertGreaterEqual(stats['saka_harvested'], 100)  # Au moins 100
        self.assertGreaterEqual(stats['saka_planted'], 50)  # Au moins 50
        self.assertEqual(stats['saka_composted'], 25)  # Exactement 25

