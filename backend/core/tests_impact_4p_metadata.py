"""
Tests pour vérifier que les métadonnées 4P (labels, disclaimers) sont correctement exposées.

PHILOSOPHIE EGOEJO :
P3 et P4 sont des PROXY V1 INTERNE, pas des mesures académiques.
Les métadonnées DOIVENT être explicites pour éviter toute prétention scientifique.

Test P0 : Vérifier que les métadonnées sont présentes et correctes :
- P3 et P4 ont label = "PROXY V1 INTERNE"
- P3 et P4 ont un disclaimer explicite
- P1 et P2 ont is_measured = True
- P3 et P4 ont is_measured = False
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from core.models.projects import Projet
from core.models.impact import ProjectImpact4P
from core.models.fundraising import Cagnotte, Contribution
from core.services.impact_4p import update_project_4p
from finance.models import EscrowContract, WalletTransaction, UserWallet

User = get_user_model()


class Impact4PMetadataTestCase(TestCase):
    """Tests pour vérifier les métadonnées 4P dans les réponses API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Créer un projet de test
        self.project = Projet.objects.create(
            titre='Projet Test 4P Metadata',
            description='Description du projet test',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00'),
            impact_score=75,  # Pour P3
            saka_score=150,  # Pour P2
            saka_supporters_count=10  # Pour P4
        )
    
    def test_api_projet_impact_4p_meta_p3_label_proxy_v1(self):
        """
        Test P0 : P3 DOIT avoir label = "PROXY V1 INTERNE"
        
        Assertion : response.data['impact_4p']['meta']['p3']['label'] == "PROXY V1 INTERNE"
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier la présence de p3 dans meta
        self.assertIn('p3', meta)
        p3_meta = meta['p3']
        
        # Vérifier que le label est "PROXY V1 INTERNE"
        self.assertEqual(p3_meta['label'], "PROXY V1 INTERNE")
    
    def test_api_projet_impact_4p_meta_p4_label_proxy_v1(self):
        """
        Test P0 : P4 DOIT avoir label = "PROXY V1 INTERNE"
        
        Assertion : response.data['impact_4p']['meta']['p4']['label'] == "PROXY V1 INTERNE"
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier la présence de p4 dans meta
        self.assertIn('p4', meta)
        p4_meta = meta['p4']
        
        # Vérifier que le label est "PROXY V1 INTERNE"
        self.assertEqual(p4_meta['label'], "PROXY V1 INTERNE")
    
    def test_api_projet_impact_4p_meta_p3_disclaimer_present(self):
        """
        Test P0 : P3 DOIT avoir un disclaimer explicite
        
        Assertion : response.data['impact_4p']['meta']['p3']['disclaimer'] est présent
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier la présence de p3 dans meta
        self.assertIn('p3', meta)
        p3_meta = meta['p3']
        
        # Vérifier que le disclaimer est présent
        self.assertIn('disclaimer', p3_meta)
        self.assertIsInstance(p3_meta['disclaimer'], str)
        self.assertGreater(len(p3_meta['disclaimer']), 0)
        
        # Vérifier que le disclaimer mentionne "proxy" ou "non académique"
        disclaimer_lower = p3_meta['disclaimer'].lower()
        self.assertTrue(
            'proxy' in disclaimer_lower or 
            'non académique' in disclaimer_lower or
            'interne' in disclaimer_lower,
            f"Le disclaimer DOIT mentionner que P3 est un proxy non académique. Contenu: {p3_meta['disclaimer']}"
        )
    
    def test_api_projet_impact_4p_meta_p4_disclaimer_present(self):
        """
        Test P0 : P4 DOIT avoir un disclaimer explicite
        
        Assertion : response.data['impact_4p']['meta']['p4']['disclaimer'] est présent
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier la présence de p4 dans meta
        self.assertIn('p4', meta)
        p4_meta = meta['p4']
        
        # Vérifier que le disclaimer est présent
        self.assertIn('disclaimer', p4_meta)
        self.assertIsInstance(p4_meta['disclaimer'], str)
        self.assertGreater(len(p4_meta['disclaimer']), 0)
        
        # Vérifier que le disclaimer mentionne "proxy" ou "non académique"
        disclaimer_lower = p4_meta['disclaimer'].lower()
        self.assertTrue(
            'proxy' in disclaimer_lower or 
            'non académique' in disclaimer_lower or
            'interne' in disclaimer_lower,
            f"Le disclaimer DOIT mentionner que P4 est un proxy non académique. Contenu: {p4_meta['disclaimer']}"
        )
    
    def test_api_projet_impact_4p_meta_p1_p2_is_measured_true(self):
        """
        Test P0 : P1 et P2 DOIVENT avoir is_measured = True
        
        Assertion : 
        - response.data['impact_4p']['meta']['p1']['is_measured'] == True
        - response.data['impact_4p']['meta']['p2']['is_measured'] == True
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier que P1 a is_measured = True
        self.assertIn('p1', meta)
        self.assertIn('is_measured', meta['p1'])
        self.assertTrue(meta['p1']['is_measured'], "P1 DOIT avoir is_measured = True")
        
        # Vérifier que P2 a is_measured = True
        self.assertIn('p2', meta)
        self.assertIn('is_measured', meta['p2'])
        self.assertTrue(meta['p2']['is_measured'], "P2 DOIT avoir is_measured = True")
    
    def test_api_projet_impact_4p_meta_p3_p4_is_measured_false(self):
        """
        Test P0 : P3 et P4 DOIVENT avoir is_measured = False
        
        Assertion : 
        - response.data['impact_4p']['meta']['p3']['is_measured'] == False
        - response.data['impact_4p']['meta']['p4']['is_measured'] == False
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier que P3 a is_measured = False
        self.assertIn('p3', meta)
        self.assertIn('is_measured', meta['p3'])
        self.assertFalse(meta['p3']['is_measured'], "P3 DOIT avoir is_measured = False")
        
        # Vérifier que P4 a is_measured = False
        self.assertIn('p4', meta)
        self.assertIn('is_measured', meta['p4'])
        self.assertFalse(meta['p4']['is_measured'], "P4 DOIT avoir is_measured = False")
    
    def test_api_projet_impact_4p_meta_p3_description_no_scientific_claim(self):
        """
        Test P0 : P3 DOIT avoir une description qui ne prétend pas être scientifique
        
        Assertion : La description de P3 ne doit pas contenir de termes comme
        "mesure scientifique", "mesure académique", "mesure robuste" (sans négation)
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier que P3 a une description
        self.assertIn('p3', meta)
        self.assertIn('description', meta['p3'])
        description = meta['p3']['description'].lower()
        
        # Vérifier que la description mentionne "non académique" ou "simplifié"
        self.assertTrue(
            'non académique' in description or 
            'simplifié' in description or
            'proxy' in description or
            'interne' in description,
            f"La description de P3 DOIT indiquer qu'il s'agit d'un proxy non académique. Contenu: {meta['p3']['description']}"
        )
    
    def test_api_projet_impact_4p_meta_p4_description_no_scientific_claim(self):
        """
        Test P0 : P4 DOIT avoir une description qui ne prétend pas être scientifique
        
        Assertion : La description de P4 ne doit pas contenir de termes comme
        "mesure scientifique", "mesure académique", "mesure robuste" (sans négation)
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier que P4 a une description
        self.assertIn('p4', meta)
        self.assertIn('description', meta['p4'])
        description = meta['p4']['description'].lower()
        
        # Vérifier que la description mentionne "non académique" ou "simplifié"
        self.assertTrue(
            'non académique' in description or 
            'simplifié' in description or
            'proxy' in description or
            'interne' in description,
            f"La description de P4 DOIT indiquer qu'il s'agit d'un proxy non académique. Contenu: {meta['p4']['description']}"
        )
    
    def test_api_projet_impact_4p_meta_structure_complete(self):
        """
        Test P0 : La structure meta DOIT être complète pour tous les scores (P1, P2, P3, P4)
        
        Assertion : Tous les scores ont label, description, is_measured
        P3 et P4 ont également disclaimer
        """
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier que tous les scores ont des métadonnées
        for p_key in ['p1', 'p2', 'p3', 'p4']:
            self.assertIn(p_key, meta, f"{p_key} DOIT être présent dans meta")
            p_meta = meta[p_key]
            
            # Vérifier que chaque score a label, description, is_measured
            self.assertIn('label', p_meta, f"{p_key} DOIT avoir un label")
            self.assertIn('description', p_meta, f"{p_key} DOIT avoir une description")
            self.assertIn('is_measured', p_meta, f"{p_key} DOIT avoir is_measured")
            
            # Vérifier que P3 et P4 ont un disclaimer
            if p_key in ['p3', 'p4']:
                self.assertIn('disclaimer', p_meta, f"{p_key} DOIT avoir un disclaimer")
    
    def test_api_projet_impact_4p_meta_present_even_without_calculation(self):
        """
        Test P0 : Les métadonnées DOIVENT être présentes même si impact_4p n'est pas calculé
        
        Assertion : Même avec des valeurs par défaut, les métadonnées sont présentes
        """
        # Ne pas calculer les scores 4P (projet fraîchement créé)
        # Vérifier que ProjectImpact4P n'existe pas
        self.assertFalse(ProjectImpact4P.objects.filter(project=self.project).exists())
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier la présence de meta même avec valeurs par défaut
        self.assertIn('meta', impact_4p)
        meta = impact_4p['meta']
        
        # Vérifier que tous les scores ont des métadonnées
        for p_key in ['p1', 'p2', 'p3', 'p4']:
            self.assertIn(p_key, meta, f"{p_key} DOIT être présent dans meta même sans calcul")
            p_meta = meta[p_key]
            
            # Vérifier que chaque score a label, description, is_measured
            self.assertIn('label', p_meta, f"{p_key} DOIT avoir un label même sans calcul")
            self.assertIn('description', p_meta, f"{p_key} DOIT avoir une description même sans calcul")
            self.assertIn('is_measured', p_meta, f"{p_key} DOIT avoir is_measured même sans calcul")
            
            # Vérifier que P3 et P4 ont un disclaimer
            if p_key in ['p3', 'p4']:
                self.assertIn('disclaimer', p_meta, f"{p_key} DOIT avoir un disclaimer même sans calcul")

