"""
Tests pour les endpoints API Engagement.

Vérifie que les endpoints de gestion des engagements d'aide fonctionnent correctement :
- Liste des engagements (avec filtrage)
- Création d'un engagement
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Engagement, HelpRequest

User = get_user_model()


class EngagementTestCase(TestCase):
    """Tests pour les endpoints d'engagements d'aide"""

    def setUp(self):
        """Prépare les données de test"""
        self.client = APIClient()

        # Créer des utilisateurs
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Créer une demande d'aide
        self.help_request = HelpRequest.objects.create(
            title="Besoin d'aide pour un projet",
            description="Description du besoin",
            user=self.user,
            status="new"
        )

        # Créer des engagements
        self.engagement1 = Engagement.objects.create(
            user=self.user,
            help_request=self.help_request,
            help_types=["competences"],
            domains=["developpement"],
            availability="weekends",
            scope="local",
            anonymity="pseudo",
            notes="Je peux aider avec mes compétences",
            status="new"
        )

        self.engagement2 = Engagement.objects.create(
            user=self.other_user,
            help_types=["financier"],
            domains=["finance"],
            availability="flexible",
            scope="both",
            anonymity="team_only",
            notes="Je peux aider financièrement",
            status="active"
        )

    def test_list_engagements_all(self):
        """Test la liste de tous les engagements"""
        response = self.client.get('/api/engagements/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

        # Vérifier que les deux engagements sont présents
        engagement_ids = [item['id'] for item in response.data]
        self.assertIn(self.engagement1.id, engagement_ids)
        self.assertIn(self.engagement2.id, engagement_ids)

    def test_list_engagements_filtered_by_help_request(self):
        """Test le filtrage des engagements par demande d'aide"""
        response = self.client.get(f'/api/engagements/?help_request={self.help_request.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.engagement1.id)
        self.assertEqual(response.data[0]['help_request'], self.help_request.id)

    def test_list_engagements_filtered_by_nonexistent_help_request(self):
        """Test le filtrage avec une demande d'aide inexistante"""
        response = self.client.get('/api/engagements/?help_request=99999')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_engagement_authenticated(self):
        """Test la création d'un engagement par un utilisateur authentifié"""
        self.client.force_authenticate(user=self.user)

        data = {
            'help_request': self.help_request.id,
            'help_types': ['temps', 'competences'],
            'domains': ['developpement', 'design'],
            'availability': 'weekends',
            'scope': 'local',
            'anonymity': 'pseudo',
            'notes': 'Je peux aider avec mon temps et mes compétences',
        }

        response = self.client.post('/api/engagements/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['help_request'], self.help_request.id)
        self.assertEqual(response.data['status'], 'new')
        self.assertEqual(response.data['help_types'], ['temps', 'competences'])

        # Vérifier que l'engagement existe en base
        engagement = Engagement.objects.get(id=response.data['id'])
        self.assertEqual(engagement.user, self.user)
        self.assertEqual(engagement.status, 'new')

    def test_create_engagement_unauthenticated(self):
        """Test la création d'un engagement par un utilisateur non authentifié"""
        data = {
            'help_types': ['materiel'],
            'domains': ['equipement'],
            'availability': 'flexible',
            'scope': 'both',
            'anonymity': 'pseudo',
            'notes': 'Je peux fournir du matériel',
        }

        response = self.client.post('/api/engagements/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get('user'))  # User doit être null

        # Vérifier que l'engagement existe en base
        engagement = Engagement.objects.get(id=response.data['id'])
        self.assertIsNone(engagement.user)
        self.assertEqual(engagement.status, 'new')

    def test_create_engagement_without_help_request(self):
        """Test la création d'un engagement sans demande d'aide spécifique"""
        self.client.force_authenticate(user=self.user)

        data = {
            'help_types': ['financier'],
            'domains': ['finance'],
            'availability': 'flexible',
            'scope': 'international',
            'anonymity': 'team_only',
            'notes': 'Offre générale d\'aide financière',
        }

        response = self.client.post('/api/engagements/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get('help_request'))

        # Vérifier que l'engagement existe en base
        engagement = Engagement.objects.get(id=response.data['id'])
        self.assertIsNone(engagement.help_request)

    def test_create_engagement_invalid_data(self):
        """Test la création d'un engagement avec des données invalides"""
        self.client.force_authenticate(user=self.user)

        data = {
            'help_types': [],  # Liste vide (invalide si requis)
            'scope': 'invalid_scope',  # Scope invalide
        }

        response = self.client.post('/api/engagements/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_engagements_ordered_by_created_at_desc(self):
        """Test que les engagements sont triés par date de création décroissante"""
        # Créer un nouvel engagement
        new_engagement = Engagement.objects.create(
            user=self.user,
            help_types=['financier'],
            domains=['finance'],
            availability='flexible',
            scope='both',
            anonymity='pseudo',
            notes='Nouvel engagement',
            status='new'
        )

        response = self.client.get('/api/engagements/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Le premier élément devrait être le plus récent
        self.assertEqual(response.data[0]['id'], new_engagement.id)

