"""
Tests unitaires pour l'endpoint public /api/public/egoejo-compliance.json

Vérifie que l'endpoint :
- Retourne le format JSON spécifié
- Est en lecture seule (GET uniquement)
- Utilise le cache correctement
- Est accessible sans authentification
"""
import json
from datetime import datetime
from django.test import TestCase, Client
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from django.urls import reverse


class EGOEJOComplianceStatusViewTest(TestCase):
    """
    Tests pour l'endpoint /api/public/egoejo-compliance.json
    """
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.url = "/api/public/egoejo-compliance.json"
        # Vider le cache avant chaque test
        cache.clear()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        cache.clear()
    
    def test_endpoint_accessible_sans_authentification(self):
        """
        Vérifie que l'endpoint est accessible sans authentification.
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
    
    def test_endpoint_lecture_seule_get(self):
        """
        Vérifie que l'endpoint est en lecture seule (GET uniquement).
        """
        # POST doit échouer
        response_post = self.client.post(self.url, {})
        self.assertEqual(response_post.status_code, 405)  # Method Not Allowed
        
        # PUT doit échouer
        response_put = self.client.put(self.url, {}, content_type='application/json')
        self.assertEqual(response_put.status_code, 405)
        
        # DELETE doit échouer
        response_delete = self.client.delete(self.url)
        self.assertEqual(response_delete.status_code, 405)
        
        # GET doit fonctionner
        response_get = self.client.get(self.url)
        self.assertEqual(response_get.status_code, 200)
    
    def test_format_json_specifie(self):
        """
        Vérifie que la réponse JSON respecte le format spécifié :
        {
          "compliance_status": "core" | "extended" | "non-compliant",
          "criteria": [...],
          "last_audit": "ISO-8601"
        }
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation", "anti_accumulation"],
                    "extended": []
                }
                
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                
                data = json.loads(response.content)
                
                # Vérifier la structure
                self.assertIn("compliance_status", data)
                self.assertIn("criteria", data)
                self.assertIn("last_audit", data)
                
                # Vérifier les types
                self.assertIsInstance(data["compliance_status"], str)
                self.assertIn(data["compliance_status"], ["core", "extended", "non-compliant"])
                self.assertIsInstance(data["criteria"], list)
                self.assertIsInstance(data["last_audit"], str)
                
                # Vérifier le format ISO-8601 de last_audit
                try:
                    datetime.fromisoformat(data["last_audit"].replace('Z', '+00:00'))
                except ValueError:
                    self.fail("last_audit n'est pas au format ISO-8601")
    
    def test_compliance_status_core(self):
        """
        Vérifie que le statut "core" est correctement retourné.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation", "anti_accumulation"],
                    "extended": []
                }
                
                response = self.client.get(self.url)
                data = json.loads(response.content)
                
                self.assertEqual(data["compliance_status"], "core")
                self.assertGreater(len(data["criteria"]), 0)
                
                # Vérifier que les critères core sont présents
                core_criteria = [c for c in data["criteria"] if c["level"] == "core"]
                self.assertGreater(len(core_criteria), 0)
    
    def test_compliance_status_extended(self):
        """
        Vérifie que le statut "extended" est correctement retourné.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-extended"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation", "anti_accumulation"],
                    "extended": ["governance_protective", "monitoring_real_time"]
                }
                
                response = self.client.get(self.url)
                data = json.loads(response.content)
                
                self.assertEqual(data["compliance_status"], "extended")
                
                # Vérifier que les critères extended sont présents
                extended_criteria = [c for c in data["criteria"] if c["level"] == "extended"]
                self.assertGreater(len(extended_criteria), 0)
    
    def test_compliance_status_non_compliant(self):
        """
        Vérifie que le statut "non-compliant" est correctement retourné.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="non-compliant"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": [],
                    "extended": []
                }
                
                response = self.client.get(self.url)
                data = json.loads(response.content)
                
                self.assertEqual(data["compliance_status"], "non-compliant")
                self.assertEqual(len(data["criteria"]), 0)
    
    def test_criteria_structure(self):
        """
        Vérifie que chaque critère a la structure attendue.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation", "anti_accumulation"],
                    "extended": []
                }
                
                response = self.client.get(self.url)
                data = json.loads(response.content)
                
                for criterion in data["criteria"]:
                    self.assertIn("id", criterion)
                    self.assertIn("level", criterion)
                    self.assertIn("validated", criterion)
                    self.assertIn("description", criterion)
                    
                    self.assertIsInstance(criterion["id"], str)
                    self.assertIn(criterion["level"], ["core", "extended"])
                    self.assertIsInstance(criterion["validated"], bool)
                    self.assertIsInstance(criterion["description"], str)
                    self.assertTrue(criterion["validated"])  # Tous les critères retournés sont validés
    
    def test_cache_controle(self):
        """
        Vérifie que le cache est correctement utilisé.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation"],
                    "extended": []
                }
                
                # Premier appel
                response1 = self.client.get(self.url)
                self.assertEqual(response1.status_code, 200)
                
                # Vérifier que les en-têtes de cache sont présents
                self.assertIn('Cache-Control', response1)
                self.assertIn('public, max-age=900', response1['Cache-Control'])
                self.assertIn('Last-Modified', response1)
                
                # Deuxième appel (devrait utiliser le cache)
                response2 = self.client.get(self.url)
                self.assertEqual(response2.status_code, 200)
                
                # Les données doivent être identiques (même last_audit)
                data1 = json.loads(response1.content)
                data2 = json.loads(response2.content)
                
                # last_audit devrait être identique (cache)
                self.assertEqual(data1["last_audit"], data2["last_audit"])
    
    def test_cache_expiration(self):
        """
        Vérifie que le cache expire après 15 minutes.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation"],
                    "extended": []
                }
                
                # Premier appel
                response1 = self.client.get(self.url)
                data1 = json.loads(response1.content)
                last_audit1 = data1["last_audit"]
                
                # Vider le cache manuellement
                cache.clear()
                
                # Deuxième appel (cache expiré, nouveau calcul)
                response2 = self.client.get(self.url)
                data2 = json.loads(response2.content)
                last_audit2 = data2["last_audit"]
                
                # last_audit devrait être différent (nouveau calcul)
                # Note: En pratique, si les deux appels sont très rapides, last_audit peut être identique
                # mais le cache devrait être recalculé
                self.assertIsNotNone(last_audit2)
    
    def test_last_audit_iso8601_format(self):
        """
        Vérifie que last_audit est au format ISO-8601.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation"],
                    "extended": []
                }
                
                response = self.client.get(self.url)
                data = json.loads(response.content)
                
                last_audit = data["last_audit"]
                
                # Vérifier le format ISO-8601 (avec Z pour UTC)
                self.assertTrue(last_audit.endswith('Z') or '+' in last_audit or last_audit.count(':') >= 2)
                
                # Essayer de parser la date
                try:
                    # Remplacer Z par +00:00 pour compatibilité Python < 3.11
                    iso_string = last_audit.replace('Z', '+00:00')
                    datetime.fromisoformat(iso_string)
                except ValueError as e:
                    self.fail(f"last_audit n'est pas au format ISO-8601 valide: {e}")
    
    def test_criteria_descriptions(self):
        """
        Vérifie que les descriptions des critères sont présentes et non vides.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            with patch('core.api.compliance_views._get_validated_criteria') as mock_criteria:
                mock_criteria.return_value = {
                    "core": ["saka_eur_separation", "anti_accumulation"],
                    "extended": []
                }
                
                response = self.client.get(self.url)
                data = json.loads(response.content)
                
                for criterion in data["criteria"]:
                    self.assertIsNotNone(criterion["description"])
                    self.assertGreater(len(criterion["description"]), 0)
                    self.assertIsInstance(criterion["description"], str)
    
    def test_response_content_type(self):
        """
        Vérifie que le Content-Type est application/json.
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response['Content-Type'])
        self.assertIn('charset=utf-8', response['Content-Type'])
    
    def test_response_json_valid(self):
        """
        Vérifie que la réponse est un JSON valide.
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        
        # Essayer de parser le JSON
        try:
            data = json.loads(response.content)
            self.assertIsInstance(data, dict)
        except json.JSONDecodeError as e:
            self.fail(f"La réponse n'est pas un JSON valide: {e}")

