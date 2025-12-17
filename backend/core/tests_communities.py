"""
Tests pour le modèle Community et l'API associée.
V1 : Structure minimale pour préparer la subsidiarité.
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models.communities import Community
from core.models.projects import Projet

User = get_user_model()


class CommunityTestCase(TestCase):
    """Tests pour le modèle Community"""
    
    def setUp(self):
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
    
    def test_create_community(self):
        """Test la création d'une communauté"""
        community = Community.objects.create(
            name="Communauté Test",
            description="Une communauté de test",
            is_active=True
        )
        
        self.assertEqual(community.name, "Communauté Test")
        self.assertEqual(community.slug, "communaute-test")  # Auto-généré
        self.assertEqual(community.description, "Une communauté de test")
        self.assertTrue(community.is_active)
        self.assertIsNotNone(community.created_at)
    
    def test_community_slug_auto_generation(self):
        """Test que le slug est auto-généré si vide"""
        community = Community.objects.create(
            name="Ma Super Communauté"
        )
        
        self.assertEqual(community.slug, "ma-super-communaute")
    
    def test_community_slug_unique(self):
        """Test que le slug doit être unique"""
        Community.objects.create(
            name="Test",
            slug="test"
        )
        
        # Tentative de créer une deuxième communauté avec le même slug
        with self.assertRaises(Exception):  # IntegrityError ou ValidationError
            Community.objects.create(
                name="Test 2",
                slug="test"
            )
    
    def test_community_members(self):
        """Test l'ajout de membres à une communauté"""
        community = Community.objects.create(
            name="Communauté avec Membres"
        )
        
        # Ajouter des membres
        community.members.add(self.user1, self.user2)
        
        self.assertEqual(community.members.count(), 2)
        self.assertIn(self.user1, community.members.all())
        self.assertIn(self.user2, community.members.all())
        
        # Vérifier la relation inverse
        self.assertIn(community, self.user1.communities.all())
    
    def test_project_community_association(self):
        """Test l'association d'un projet à une communauté"""
        community = Community.objects.create(
            name="Communauté Projets"
        )
        
        project = Projet.objects.create(
            titre="Projet Test",
            description="Description du projet",
            community=community
        )
        
        self.assertEqual(project.community, community)
        self.assertEqual(community.projects.count(), 1)
        self.assertIn(project, community.projects.all())
    
    def test_project_without_community(self):
        """Test qu'un projet peut exister sans communauté (nullable)"""
        project = Projet.objects.create(
            titre="Projet Sans Communauté",
            description="Description"
        )
        
        self.assertIsNone(project.community)
    
    def test_community_deletion_set_null(self):
        """Test que la suppression d'une communauté met community à NULL sur les projets"""
        community = Community.objects.create(
            name="Communauté à Supprimer"
        )
        
        project = Projet.objects.create(
            titre="Projet Associé",
            description="Description",
            community=community
        )
        
        # Supprimer la communauté
        community.delete()
        
        # Recharger le projet depuis la DB
        project.refresh_from_db()
        self.assertIsNone(project.community)


class CommunityAPITestCase(TestCase):
    """Tests pour l'API des communautés"""
    
    def setUp(self):
        self.client = TestCase.client_class()
        
        self.community1 = Community.objects.create(
            name="Communauté Active",
            description="Description active",
            is_active=True
        )
        
        self.community2 = Community.objects.create(
            name="Communauté Inactive",
            description="Description inactive",
            is_active=False
        )
        
        # Créer un projet associé
        self.project = Projet.objects.create(
            titre="Projet Communauté",
            description="Description",
            community=self.community1
        )
    
    def test_api_community_list(self):
        """Test GET /api/communities/ retourne uniquement les communautés actives"""
        response = self.client.get('/api/communities/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Vérifier que c'est une liste
        self.assertIsInstance(data, list)
        
        # Vérifier qu'il n'y a qu'une seule communauté active
        self.assertEqual(len(data), 1)
        
        # Vérifier la structure
        community_data = data[0]
        self.assertIn('id', community_data)
        self.assertIn('name', community_data)
        self.assertIn('slug', community_data)
        self.assertIn('description', community_data)
        self.assertIn('is_active', community_data)
        self.assertIn('created_at', community_data)
        self.assertIn('members_count', community_data)
        self.assertIn('projects_count', community_data)
        
        # Vérifier les valeurs
        self.assertEqual(community_data['name'], "Communauté Active")
        self.assertEqual(community_data['is_active'], True)
        self.assertEqual(community_data['projects_count'], 1)
    
    def test_api_community_detail(self):
        """Test GET /api/communities/<slug>/ retourne les détails"""
        response = self.client.get(f'/api/communities/{self.community1.slug}/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Vérifier la structure
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('slug', data)
        self.assertIn('description', data)
        self.assertIn('is_active', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('members_count', data)
        self.assertIn('projects_count', data)
        self.assertIn('projects', data)
        
        # Vérifier les valeurs
        self.assertEqual(data['name'], "Communauté Active")
        self.assertEqual(data['slug'], self.community1.slug)
        self.assertEqual(data['projects_count'], 1)
        
        # Vérifier la liste des projets
        self.assertIsInstance(data['projects'], list)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['id'], self.project.id)
        self.assertEqual(data['projects'][0]['titre'], "Projet Communauté")
    
    def test_api_community_detail_not_found(self):
        """Test GET /api/communities/<slug>/ retourne 404 si la communauté n'existe pas"""
        response = self.client.get('/api/communities/non-existent/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_api_community_detail_inactive(self):
        """Test GET /api/communities/<slug>/ retourne 404 si la communauté est inactive"""
        response = self.client.get(f'/api/communities/{self.community2.slug}/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_api_community_list_unauthenticated(self):
        """Test que l'API est accessible sans authentification (AllowAny)"""
        # Ne pas se connecter
        response = self.client.get('/api/communities/')
        
        self.assertEqual(response.status_code, 200)

