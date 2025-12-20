"""
Tests pour l'architecture des Oracles d'Impact
"""

from django.test import TestCase
from decimal import Decimal

from core.models.projects import Projet
from core.services.impact_oracles import (
    BaseImpactOracle,
    CO2AvoidedOracle,
    SocialImpactOracle,
    get_oracle,
    ORACLE_REGISTRY,
    OracleError,
)
from core.services.oracle_manager import OracleManager


class BaseImpactOracleTestCase(TestCase):
    """Tests pour la classe abstraite BaseImpactOracle"""
    
    def test_base_oracle_cannot_be_instanciated(self):
        """Test que BaseImpactOracle ne peut pas être instanciée directement"""
        with self.assertRaises(TypeError):
            BaseImpactOracle()


class CO2AvoidedOracleTestCase(TestCase):
    """Tests pour CO2AvoidedOracle"""
    
    def setUp(self):
        self.project = Projet.objects.create(
            titre="Projet Test CO2",
            description="Projet de test pour l'oracle CO2",
            categorie="energie"
        )
        self.oracle = CO2AvoidedOracle()
    
    def test_oracle_info(self):
        """Test que l'oracle retourne ses informations"""
        info = self.oracle.get_oracle_info()
        self.assertEqual(info['oracle_id'], 'co2_avoided')
        self.assertEqual(info['name'], 'Oracle CO2 Évité')
        self.assertIn('P3', info['impact_dimensions'])
    
    def test_fetch_impact_data(self):
        """Test la récupération des données d'impact"""
        data = self.oracle.fetch_impact_data(self.project)
        
        self.assertIn('raw_data', data)
        self.assertIn('timestamp', data)
        self.assertIn('source', data)
        self.assertIn('status', data)
        self.assertEqual(data['source'], 'co2_avoided')
        
        if data['status'] == 'success':
            self.assertIn('co2_avoided_kg', data['raw_data'])
    
    def test_get_impact_metrics(self):
        """Test l'extraction des métriques"""
        # Simuler des données
        data = {
            'raw_data': {
                'co2_avoided_kg': 500.0,
                'confidence': 0.7,
                'calculation_method': 'simulated',
            },
            'timestamp': '2025-12-19T10:00:00Z',
            'source': 'co2_avoided',
            'status': 'success',
        }
        
        metrics = self.oracle.get_impact_metrics(data)
        
        self.assertIn('p3_contributions', metrics)
        self.assertIn('co2_avoided_kg', metrics['p3_contributions'])
        self.assertIn('co2_score', metrics['p3_contributions'])
        self.assertIn('metadata', metrics)


class SocialImpactOracleTestCase(TestCase):
    """Tests pour SocialImpactOracle"""
    
    def setUp(self):
        self.project = Projet.objects.create(
            titre="Projet Test Social",
            description="Projet de test pour l'oracle social" * 10,  # Description longue
            categorie="social"
        )
        self.oracle = SocialImpactOracle()
    
    def test_oracle_info(self):
        """Test que l'oracle retourne ses informations"""
        info = self.oracle.get_oracle_info()
        self.assertEqual(info['oracle_id'], 'social_impact')
        self.assertIn('P3', info['impact_dimensions'])
        self.assertIn('P4', info['impact_dimensions'])
    
    def test_fetch_impact_data(self):
        """Test la récupération des données d'impact"""
        data = self.oracle.fetch_impact_data(self.project)
        
        self.assertIn('raw_data', data)
        self.assertEqual(data['source'], 'social_impact')
        
        if data['status'] == 'success':
            self.assertIn('people_impacted', data['raw_data'])
            self.assertIn('jobs_created', data['raw_data'])
    
    def test_get_impact_metrics(self):
        """Test l'extraction des métriques"""
        data = {
            'raw_data': {
                'people_impacted': 500,
                'jobs_created': 10,
                'confidence': 0.6,
            },
            'timestamp': '2025-12-19T10:00:00Z',
            'source': 'social_impact',
            'status': 'success',
        }
        
        metrics = self.oracle.get_impact_metrics(data)
        
        self.assertIn('p3_contributions', metrics)
        self.assertIn('p4_contributions', metrics)
        self.assertIn('people_impacted', metrics['p3_contributions'])
        self.assertIn('purpose_alignment', metrics['p4_contributions'])


class OracleRegistryTestCase(TestCase):
    """Tests pour le registre des oracles"""
    
    def test_registry_contains_oracles(self):
        """Test que le registre contient les oracles"""
        self.assertIn('co2_avoided', ORACLE_REGISTRY)
        self.assertIn('social_impact', ORACLE_REGISTRY)
    
    def test_get_oracle(self):
        """Test la factory function get_oracle"""
        oracle = get_oracle('co2_avoided')
        self.assertIsNotNone(oracle)
        self.assertIsInstance(oracle, CO2AvoidedOracle)
        
        oracle = get_oracle('social_impact')
        self.assertIsNotNone(oracle)
        self.assertIsInstance(oracle, SocialImpactOracle)
        
        oracle = get_oracle('nonexistent')
        self.assertIsNone(oracle)


class OracleManagerTestCase(TestCase):
    """Tests pour OracleManager"""
    
    def setUp(self):
        self.project = Projet.objects.create(
            titre="Projet Test Manager",
            description="Projet de test pour OracleManager",
            categorie="energie",
            active_oracles=['co2_avoided', 'social_impact']
        )
    
    def test_get_oracle_data(self):
        """Test la récupération des données de tous les oracles"""
        result = OracleManager.get_oracle_data(self.project)
        
        self.assertIn('oracles', result)
        self.assertIn('aggregated_metrics', result)
        self.assertIn('metadata', result)
        
        self.assertIn('co2_avoided', result['oracles'])
        self.assertIn('social_impact', result['oracles'])
        
        self.assertIn('p3_contributions', result['aggregated_metrics'])
        self.assertIn('p4_contributions', result['aggregated_metrics'])
    
    def test_get_available_oracles(self):
        """Test la liste des oracles disponibles"""
        oracles = OracleManager.get_available_oracles()
        
        self.assertGreater(len(oracles), 0)
        self.assertTrue(any(o['oracle_id'] == 'co2_avoided' for o in oracles))
        self.assertTrue(any(o['oracle_id'] == 'social_impact' for o in oracles))
    
    def test_project_without_oracles(self):
        """Test un projet sans oracles actifs"""
        project = Projet.objects.create(
            titre="Projet Sans Oracles",
            description="Projet sans oracles",
            active_oracles=[]
        )
        
        result = OracleManager.get_oracle_data(project)
        
        self.assertEqual(result['metadata']['oracles_count'], 0)
        self.assertEqual(len(result['oracles']), 0)


class ProjectActiveOraclesTestCase(TestCase):
    """Tests pour le champ active_oracles du modèle Projet"""
    
    def test_active_oracles_field(self):
        """Test que le champ active_oracles fonctionne"""
        project = Projet.objects.create(
            titre="Projet avec Oracles",
            description="Test",
            active_oracles=['co2_avoided', 'social_impact']
        )
        
        self.assertEqual(project.active_oracles, ['co2_avoided', 'social_impact'])
        
        # Modifier les oracles
        project.active_oracles = ['co2_avoided']
        project.save()
        
        project.refresh_from_db()
        self.assertEqual(project.active_oracles, ['co2_avoided'])
    
    def test_active_oracles_default_empty(self):
        """Test que active_oracles est vide par défaut"""
        project = Projet.objects.create(
            titre="Projet Sans Oracles",
            description="Test"
        )
        
        self.assertEqual(project.active_oracles, [])

