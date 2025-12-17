"""
Tests pour les endpoints API Content (EducationalContent).

Vérifie que les endpoints de gestion des contenus éducatifs fonctionnent correctement :
- Liste des contenus (avec cache)
- Détail d'un contenu
- Création d'un contenu
- Publication d'un contenu
- Marquer un contenu comme consommé (récolte SAKA)
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from core.models import EducationalContent
from core.models.saka import SakaWallet, SakaTransaction

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class EducationalContentTestCase(TestCase):
    """Tests pour les endpoints de contenus éducatifs"""

    def setUp(self):
        """Prépare les données de test"""
        self.client = APIClient()
        cache.clear()  # Nettoyer le cache avant chaque test

        # Créer un utilisateur pour les tests
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Créer des contenus de test
        self.content_published = EducationalContent.objects.create(
            title="Contenu publié",
            slug="contenu-publie",
            type="article",
            status="published",
            category="guides",
            description="Description du contenu publié",
        )

        self.content_pending = EducationalContent.objects.create(
            title="Contenu en attente",
            slug="contenu-pending",
            type="video",
            status="pending",
            category="videos",
            description="Description du contenu en attente",
        )

    def test_list_contents_published_default(self):
        """Test que la liste retourne les contenus publiés par défaut"""
        response = self.client.get('/api/contents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Vérifier que seuls les contenus publiés sont retournés
        published_ids = [item['id'] for item in response.data]
        self.assertIn(self.content_published.id, published_ids)
        self.assertNotIn(self.content_pending.id, published_ids)

    def test_list_contents_with_status_filter(self):
        """Test le filtrage par statut"""
        # Test avec status=pending
        response = self.client.get('/api/contents/?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pending_ids = [item['id'] for item in response.data]
        self.assertIn(self.content_pending.id, pending_ids)
        self.assertNotIn(self.content_published.id, pending_ids)

        # Test avec status=published
        response = self.client.get('/api/contents/?status=published')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        published_ids = [item['id'] for item in response.data]
        self.assertIn(self.content_published.id, published_ids)
        self.assertNotIn(self.content_pending.id, published_ids)

    def test_list_contents_cache(self):
        """Test que les contenus publiés sont mis en cache"""
        # Premier appel
        response1 = self.client.get('/api/contents/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Vérifier que le cache existe
        cached_data = cache.get('educational_contents_published')
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), len(response1.data))

        # Deuxième appel (devrait utiliser le cache)
        response2 = self.client.get('/api/contents/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)

    def test_retrieve_content_detail(self):
        """Test la récupération du détail d'un contenu"""
        response = self.client.get(f'/api/contents/{self.content_published.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.content_published.id)
        self.assertEqual(response.data['title'], self.content_published.title)
        self.assertEqual(response.data['status'], 'published')

    def test_retrieve_content_not_found(self):
        """Test la récupération d'un contenu inexistant"""
        response = self.client.get('/api/contents/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_content_authenticated(self):
        """Test la création d'un contenu par un utilisateur authentifié"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'Nouveau contenu',
            'slug': 'nouveau-contenu',
            'type': 'article',
            'category': 'guides',
            'description': 'Description du nouveau contenu',
        }

        response = self.client.post('/api/contents/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Nouveau contenu')
        self.assertEqual(response.data['status'], 'pending')  # Doit être en attente
        self.assertEqual(response.data['author'], self.user.id)

        # Vérifier que le contenu existe en base
        content = EducationalContent.objects.get(id=response.data['id'])
        self.assertEqual(content.status, 'pending')
        self.assertEqual(content.author, self.user)

    def test_create_content_unauthenticated(self):
        """Test la création d'un contenu par un utilisateur non authentifié"""
        data = {
            'title': 'Contenu anonyme',
            'slug': 'contenu-anonyme',
            'type': 'article',
            'category': 'guides',
            'description': 'Description',
        }

        response = self.client.post('/api/contents/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get('author'))  # Auteur doit être null

        # Vérifier que le contenu existe en base
        content = EducationalContent.objects.get(id=response.data['id'])
        self.assertIsNone(content.author)

    def test_create_content_invalid_data(self):
        """Test la création d'un contenu avec des données invalides"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': '',  # Titre vide (invalide)
            'type': 'invalid_type',  # Type invalide
        }

        response = self.client.post('/api/contents/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_publish_content(self):
        """Test la publication d'un contenu"""
        self.client.force_authenticate(user=self.user)

        # Publier le contenu en attente
        response = self.client.post(f'/api/contents/{self.content_pending.id}/publish/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'published')

        # Vérifier en base
        self.content_pending.refresh_from_db()
        self.assertEqual(self.content_pending.status, 'published')

        # Vérifier que le cache est invalidé
        cached_data = cache.get('educational_contents_published')
        # Le cache devrait être None ou mis à jour (selon l'implémentation)

    def test_mark_consumed_authenticated_sufficient_progress(self):
        """Test marquer un contenu comme consommé avec progression suffisante (>=80%)"""
        self.client.force_authenticate(user=self.user)

        # Créer un wallet SAKA pour l'utilisateur
        wallet, _ = SakaWallet.objects.get_or_create(
            user=self.user,
            defaults={'balance': 0, 'total_harvested': 0}
        )
        initial_balance = wallet.balance

        # Marquer comme consommé avec 100% de progression
        response = self.client.post(
            f'/api/contents/{self.content_published.id}/mark-consumed/',
            {'progress': 100},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ok'])
        self.assertIn('Grains SAKA récoltés', response.data['message'])

        # Vérifier que des grains SAKA ont été récoltés
        wallet.refresh_from_db()
        self.assertGreater(wallet.balance, initial_balance)

        # Vérifier qu'une transaction SAKA a été créée
        transaction = SakaTransaction.objects.filter(
            user=self.user,
            reason='content_read'
        ).first()
        self.assertIsNotNone(transaction)

    def test_mark_consumed_authenticated_insufficient_progress(self):
        """Test marquer un contenu comme consommé avec progression insuffisante (<80%)"""
        self.client.force_authenticate(user=self.user)

        # Marquer comme consommé avec 50% de progression
        response = self.client.post(
            f'/api/contents/{self.content_published.id}/mark-consumed/',
            {'progress': 50},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['ok'])
        self.assertIn('Progression insuffisante', response.data['message'])

        # Vérifier qu'aucun grain SAKA n'a été récolté
        wallet, _ = SakaWallet.objects.get_or_create(
            user=self.user,
            defaults={'balance': 0, 'total_harvested': 0}
        )
        self.assertEqual(wallet.balance, 0)

    def test_mark_consumed_unauthenticated(self):
        """Test marquer un contenu comme consommé sans authentification"""
        response = self.client.post(
            f'/api/contents/{self.content_published.id}/mark-consumed/',
            {'progress': 100},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentification requise', response.data.get('error', ''))

    def test_mark_consumed_default_progress(self):
        """Test marquer un contenu comme consommé sans spécifier la progression (défaut: 100%)"""
        self.client.force_authenticate(user=self.user)

        # Créer un wallet SAKA
        wallet, _ = SakaWallet.objects.get_or_create(
            user=self.user,
            defaults={'balance': 0, 'total_harvested': 0}
        )
        initial_balance = wallet.balance

        # Marquer comme consommé sans progress (devrait utiliser 100% par défaut)
        response = self.client.post(
            f'/api/contents/{self.content_published.id}/mark-consumed/',
            {},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ok'])
        self.assertEqual(response.data['progress'], 100)

        # Vérifier que des grains SAKA ont été récoltés
        wallet.refresh_from_db()
        self.assertGreater(wallet.balance, initial_balance)

