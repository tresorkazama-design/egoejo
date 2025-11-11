from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Intent, Projet, Cagnotte, Contribution
import json
import os

# Ensure base URL for email links to avoid 301 redirects in tests
os.environ.setdefault("APP_BASE_URL", "http://testserver")


class IntentTestCase(TestCase):
    """Tests pour le modèle Intent et les endpoints associés"""
    
    def setUp(self):
        self.client = Client()
        # Définir le token admin pour les tests
        os.environ['ADMIN_TOKEN'] = 'test-admin-token-123'
        os.environ['RESEND_API_KEY'] = ''  # Désactiver l'envoi d'emails en test
    
    def tearDown(self):
        # Nettoyer les variables d'environnement
        if 'ADMIN_TOKEN' in os.environ:
            del os.environ['ADMIN_TOKEN']
    
    def test_create_intent_success(self):
        """Test la création d'une intention avec des données valides"""
        data = {
            'nom': 'Test User',
            'email': 'test@example.com',
            'profil': 'je-decouvre',
            'message': 'Je souhaite découvrir EGOEJO'
        }
        response = self.client.post(
            '/api/intents/rejoindre/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ok'])
        self.assertIsNotNone(response_data['id'])
        
        # Vérifier que l'intent a été créé en base
        intent = Intent.objects.get(id=response_data['id'])
        self.assertEqual(intent.nom, 'Test User')
        self.assertEqual(intent.email, 'test@example.com')
        self.assertEqual(intent.profil, 'je-decouvre')
    
    def test_create_intent_missing_fields(self):
        """Test la création d'une intention avec des champs manquants"""
        data = {
            'nom': 'Test User',
            # email manquant
            'profil': 'je-decouvre'
        }
        response = self.client.post(
            '/api/intents/rejoindre/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ok'])
        self.assertIn('error', response_data)
    
    def test_create_intent_invalid_email(self):
        """Test la création d'une intention avec un email invalide"""
        data = {
            'nom': 'Test User',
            'email': 'invalid-email',
            'profil': 'je-decouvre'
        }
        response = self.client.post(
            '/api/intents/rejoindre/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ok'])
        self.assertIn('Email invalide', response_data['error'])
    
    def test_create_intent_message_too_long(self):
        """Test la création d'une intention avec un message trop long"""
        data = {
            'nom': 'Test User',
            'email': 'test@example.com',
            'profil': 'je-decouvre',
            'message': 'A' * 2001  # Message de plus de 2000 caractères
        }
        response = self.client.post(
            '/api/intents/rejoindre/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 413)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ok'])
    
    def test_create_intent_honeypot(self):
        """Test que le honeypot anti-spam fonctionne"""
        data = {
            'nom': 'Spam Bot',
            'email': 'spam@example.com',
            'profil': 'je-decouvre',
            'website': 'http://spam.com'  # Honeypot rempli
        }
        response = self.client.post(
            '/api/intents/rejoindre/',
            data=json.dumps(data),
            content_type='application/json'
        )
        # Devrait retourner OK mais ne pas créer d'intent
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ok'])
        self.assertIsNone(response_data['id'])
        
        # Vérifier qu'aucun intent n'a été créé
        self.assertEqual(Intent.objects.count(), 0)
    
    def test_admin_data_without_token(self):
        """Test l'accès aux données admin sans token"""
        response = self.client.get('/api/intents/admin/')
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ok'])
    
    def test_admin_data_with_invalid_token(self):
        """Test l'accès aux données admin avec un token invalide"""
        response = self.client.get(
            '/api/intents/admin/',
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ok'])
    
    def test_admin_data_with_valid_token(self):
        """Test l'accès aux données admin avec un token valide"""
        # Créer quelques intents
        Intent.objects.create(
            nom='User 1',
            email='user1@example.com',
            profil='je-decouvre'
        )
        Intent.objects.create(
            nom='User 2',
            email='user2@example.com',
            profil='je-protege'
        )
        
        response = self.client.get(
            '/api/intents/admin/',
            HTTP_AUTHORIZATION='Bearer test-admin-token-123'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ok'])
        self.assertEqual(len(response_data['rows']), 2)
    
    def test_admin_data_with_filters(self):
        """Test les filtres de l'endpoint admin"""
        # Créer des intents avec différents profils
        Intent.objects.create(
            nom='User 1',
            email='user1@example.com',
            profil='je-decouvre'
        )
        Intent.objects.create(
            nom='User 2',
            email='user2@example.com',
            profil='je-protege'
        )
        
        # Filtrer par profil
        response = self.client.get(
            '/api/intents/admin/?profil=je-decouvre',
            HTTP_AUTHORIZATION='Bearer test-admin-token-123'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ok'])
        self.assertEqual(len(response_data['rows']), 1)
        self.assertEqual(response_data['rows'][0]['profil'], 'je-decouvre')
    
    def test_admin_data_with_search(self):
        """Test la recherche dans l'endpoint admin"""
        Intent.objects.create(
            nom='John Doe',
            email='john@example.com',
            profil='je-decouvre',
            message='Hello world'
        )
        Intent.objects.create(
            nom='Jane Smith',
            email='jane@example.com',
            profil='je-protege'
        )
        
        # Rechercher par nom
        response = self.client.get(
            '/api/intents/admin/?q=John',
            HTTP_AUTHORIZATION='Bearer test-admin-token-123'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ok'])
        self.assertEqual(len(response_data['rows']), 1)
        self.assertEqual(response_data['rows'][0]['nom'], 'John Doe')
    
    def test_delete_intent_without_token(self):
        """Test la suppression d'une intention sans token"""
        intent = Intent.objects.create(
            nom='Test User',
            email='test@example.com',
            profil='je-decouvre'
        )
        response = self.client.delete(f'/api/intents/{intent.id}/delete/')
        self.assertEqual(response.status_code, 401)
        
        # Vérifier que l'intent n'a pas été supprimé
        self.assertTrue(Intent.objects.filter(id=intent.id).exists())
    
    def test_delete_intent_with_valid_token(self):
        """Test la suppression d'une intention avec un token valide"""
        intent = Intent.objects.create(
            nom='Test User',
            email='test@example.com',
            profil='je-decouvre'
        )
        response = self.client.delete(
            f'/api/intents/{intent.id}/delete/',
            HTTP_AUTHORIZATION='Bearer test-admin-token-123'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ok'])
        self.assertTrue(response_data['deleted'])
        
        # Vérifier que l'intent a été supprimé
        self.assertFalse(Intent.objects.filter(id=intent.id).exists())
    
    def test_delete_intent_not_found(self):
        """Test la suppression d'une intention inexistante"""
        response = self.client.delete(
            '/api/intents/99999/delete/',
            HTTP_AUTHORIZATION='Bearer test-admin-token-123'
        )
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ok'])
    
    def test_export_intents_without_token(self):
        """Test l'export CSV sans token"""
        response = self.client.get('/api/intents/export/')
        self.assertEqual(response.status_code, 401)
    
    def test_export_intents_with_valid_token(self):
        """Test l'export CSV avec un token valide"""
        Intent.objects.create(
            nom='Test User',
            email='test@example.com',
            profil='je-decouvre',
            message='Test message'
        )
        
        response = self.client.get(
            '/api/intents/export/',
            HTTP_AUTHORIZATION='Bearer test-admin-token-123'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('intents.csv', response['Content-Disposition'])
        
        # Vérifier le contenu CSV
        content = response.content.decode('utf-8')
        self.assertIn('Test User', content)
        self.assertIn('test@example.com', content)


class ProjetCagnotteTestCase(TestCase):
    """Tests pour les modèles Projet et Cagnotte"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_projet(self):
        """Test la création d'un projet"""
        projet = Projet.objects.create(
            titre='Test Projet',
            description='Description du test',
            categorie='Environnement'
        )
        self.assertEqual(projet.titre, 'Test Projet')
        self.assertEqual(projet.categorie, 'Environnement')
    
    def test_create_cagnotte(self):
        """Test la création d'une cagnotte"""
        projet = Projet.objects.create(
            titre='Test Projet',
            description='Description'
        )
        cagnotte = Cagnotte.objects.create(
            titre='Test Cagnotte',
            description='Description cagnotte',
            montant_cible=1000.0,
            projet=projet
        )
        self.assertEqual(cagnotte.titre, 'Test Cagnotte')
        self.assertEqual(cagnotte.montant_collecte, 0.0)
        self.assertEqual(cagnotte.projet, projet)

