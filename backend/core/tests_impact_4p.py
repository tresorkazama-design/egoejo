"""
Tests pour l'API 4P (Performance Partagée) avec métadonnées.

Test P0 : Vérifier que l'API retourne les scores 4P avec une structure stable
et que les métadonnées (docstrings, labels) indiquent clairement le statut
"PROXY V1 INTERNE" pour P3 et P4.
"""
from django.test import TestCase, override_settings
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


class Impact4PAPITestCase(TestCase):
    """Tests pour l'API 4P avec vérification des métadonnées"""
    
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
            titre='Projet Test 4P',
            description='Description du projet test',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00'),
            impact_score=75,  # Pour P3
            saka_score=150,  # Pour P2
            saka_supporters_count=10  # Pour P4
        )
    
    def test_api_projet_returns_impact_4p_structure(self):
        """
        Test P0 : L'API DOIT retourner impact_4p avec structure stable
        
        Structure attendue :
        {
            "impact_4p": {
                "p1_financier": float,
                "p2_saka": int,
                "p3_social": int,
                "p4_sens": int,
                "updated_at": str (ISO format) ou null
            }
        }
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
        
        # Vérifier la structure complète
        self.assertIn('p1_financier', impact_4p)
        self.assertIn('p2_saka', impact_4p)
        self.assertIn('p3_social', impact_4p)
        self.assertIn('p4_sens', impact_4p)
        self.assertIn('updated_at', impact_4p)
        
        # Vérifier les types
        self.assertIsInstance(impact_4p['p1_financier'], (float, int))
        self.assertIsInstance(impact_4p['p2_saka'], int)
        self.assertIsInstance(impact_4p['p3_social'], int)
        self.assertIsInstance(impact_4p['p4_sens'], int)
        # updated_at peut être None ou str
        if impact_4p['updated_at'] is not None:
            self.assertIsInstance(impact_4p['updated_at'], str)
    
    def test_api_projet_returns_default_impact_4p_if_not_calculated(self):
        """
        Test P0 : L'API DOIT retourner des valeurs par défaut si impact_4p n'est pas calculé
        
        Valeurs par défaut attendues :
        {
            "p1_financier": 0.0,
            "p2_saka": 0,
            "p3_social": 0,
            "p4_sens": 0,
            "updated_at": null
        }
        """
        # Ne pas calculer les scores 4P (projet fraîchement créé)
        # Vérifier que ProjectImpact4P n'existe pas
        self.assertFalse(ProjectImpact4P.objects.filter(project=self.project).exists())
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier le statut HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la présence de impact_4p avec valeurs par défaut
        self.assertIn('impact_4p', response.data)
        impact_4p = response.data['impact_4p']
        
        # Vérifier les valeurs par défaut
        self.assertEqual(impact_4p['p1_financier'], 0.0)
        self.assertEqual(impact_4p['p2_saka'], 0)
        self.assertEqual(impact_4p['p3_social'], 0)
        self.assertEqual(impact_4p['p4_sens'], 0)
        self.assertIsNone(impact_4p['updated_at'])
    
    def test_api_projet_impact_4p_structure_stable(self):
        """
        Test P0 : La structure impact_4p DOIT être stable (même structure pour tous les projets)
        
        MÉTADONNÉES : Vérifier que la structure est cohérente même si les valeurs changent.
        """
        # Créer un deuxième projet
        project2 = Projet.objects.create(
            titre='Projet Test 4P 2',
            description='Description du projet test 2',
            funding_type='DONATION',
            donation_goal=Decimal('3000.00'),
            impact_score=50,
            saka_score=200,
            saka_supporters_count=5
        )
        
        # Calculer les scores 4P pour les deux projets
        update_project_4p(self.project)
        update_project_4p(project2)
        
        # Appeler l'API pour les deux projets
        url1 = reverse('projet-detail', kwargs={'pk': self.project.id})
        url2 = reverse('projet-detail', kwargs={'pk': project2.id})
        
        response1 = self.client.get(url1)
        response2 = self.client.get(url2)
        
        # Vérifier que les deux réponses ont la même structure
        self.assertIn('impact_4p', response1.data)
        self.assertIn('impact_4p', response2.data)
        
        impact_4p_1 = response1.data['impact_4p']
        impact_4p_2 = response2.data['impact_4p']
        
        # Vérifier que les clés sont identiques
        self.assertEqual(set(impact_4p_1.keys()), set(impact_4p_2.keys()))
        
        # Vérifier que les types sont identiques
        for key in impact_4p_1.keys():
            self.assertEqual(type(impact_4p_1[key]), type(impact_4p_2[key]))
    
    def test_api_projet_impact_4p_metadata_proxy_v1(self):
        """
        Test P0 : Vérifier que les métadonnées (docstrings) indiquent "PROXY V1 INTERNE" pour P3 et P4
        
        MÉTADONNÉES : Les docstrings du service update_project_4p() DOIVENT mentionner
        "PROXY V1 INTERNE" pour P3 et P4, indiquant que ces scores ne sont pas académiques.
        """
        from core.services.impact_4p import update_project_4p
        import inspect
        
        # Récupérer la docstring du service
        docstring = inspect.getdoc(update_project_4p)
        
        # Vérifier que la docstring mentionne "PROXY V1 INTERNE" pour P3
        self.assertIn('PROXY V1 INTERNE', docstring)
        self.assertIn('P3', docstring.upper() or docstring)
        self.assertIn('P4', docstring.upper() or docstring)
        
        # Vérifier que la docstring mentionne "non académique" ou équivalent
        docstring_lower = docstring.lower()
        self.assertTrue(
            'non académique' in docstring_lower or 
            'simplifié' in docstring_lower or
            'proxy' in docstring_lower,
            "La docstring DOIT indiquer que P3/P4 sont des proxies non académiques"
        )
    
    def test_api_projet_impact_4p_p1_p2_based_on_real_data(self):
        """
        Test P0 : P1 et P2 DOIVENT être basés sur des données réelles (traçables)
        
        P1 (financial_score) : Somme des contributions + escrows
        P2 (saka_score) : Score SAKA du projet (déjà calculé)
        """
        # Créer des données réelles pour P1
        wallet, _ = UserWallet.objects.get_or_create(user=self.user)
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        # Créer un escrow pour ce projet via le service (nécessite pledge_transaction)
        from finance.services import pledge_funds
        escrow = pledge_funds(
            user=self.user,
            project=self.project,
            amount=Decimal('200.00'),
            pledge_type='DONATION'
        )
        
        # Créer une cagnotte avec contribution
        cagnotte = Cagnotte.objects.create(
            projet=self.project,
            titre='Cagnotte Test',
            description='Description de la cagnotte test',
            montant_cible=1000.0
        )
        Contribution.objects.create(
            cagnotte=cagnotte,
            user=self.user,
            montant=Decimal('100.00')
        )
        
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier que P1 est basé sur les données réelles
        impact_4p = response.data['impact_4p']
        expected_p1 = 200.00 + 100.00  # Escrow + Contribution
        self.assertAlmostEqual(impact_4p['p1_financier'], expected_p1, places=2)
        
        # Vérifier que P2 est basé sur le saka_score du projet
        self.assertEqual(impact_4p['p2_saka'], self.project.saka_score)
    
    def test_api_projet_impact_4p_p3_p4_proxy_v1(self):
        """
        Test P0 : P3 et P4 DOIVENT être des proxies V1 (formules simplifiées)
        
        P3 (social_score) : Utilise impact_score du projet (ou 0)
        P4 (purpose_score) : Formule simplifiée (supporters_count * 10) + (cagnottes * 5)
        """
        # Configurer le projet avec des valeurs pour P3 et P4
        self.project.impact_score = 75
        self.project.saka_supporters_count = 10
        self.project.save()
        
        # Créer une cagnotte pour P4
        cagnotte = Cagnotte.objects.create(
            projet=self.project,
            titre='Cagnotte Test',
            description='Description de la cagnotte test',
            montant_cible=1000.0
        )
        
        # Calculer les scores 4P
        update_project_4p(self.project)
        
        # Appeler l'API
        url = reverse('projet-detail', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        
        # Vérifier que P3 utilise impact_score
        impact_4p = response.data['impact_4p']
        self.assertEqual(impact_4p['p3_social'], self.project.impact_score)
        
        # Vérifier que P4 utilise la formule simplifiée
        expected_p4 = (self.project.saka_supporters_count * 10) + (1 * 5)  # 1 cagnotte
        self.assertEqual(impact_4p['p4_sens'], expected_p4)
        
        # Vérifier que P3 et P4 ne sont pas des calculs complexes (proxies simples)
        # P3 = impact_score (direct)
        # P4 = formule linéaire simple
        # Ces valeurs sont des proxies, pas des mesures académiques robustes

