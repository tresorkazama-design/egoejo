"""
Tests pour les endpoints publics de constitution EGOEJO.

Vérifie que l'API ne renvoie JAMAIS "compliant" si :
- Le rapport est absent
- La signature est invalide
- Le rapport est vieux de > 24h
"""

import pytest
import json
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, mock_open


class PublicConstitutionEndpointsTest(TestCase):
    """Tests pour les endpoints publics de constitution"""
    
    def setUp(self):
        """Configuration initiale"""
        self.json_url = reverse('egoejo-constitution-status')
        self.svg_url = reverse('egoejo-constitution-badge')
    
    def _create_valid_report(self, age_hours=0) -> dict:
        """Crée un rapport de compliance valide"""
        from django.conf import settings
        import os
        
        last_check = (datetime.now(timezone.utc) - timedelta(hours=age_hours)).isoformat()
        
        report = {
            "status": "compliant",
            "version": "1.0.0",
            "last_check": last_check,
            "checks": {
                "saka_separation": True,
                "anti_accumulation": True
            }
        }
        
        # Calculer la signature
        secret = os.environ.get('COMPLIANCE_SIGNATURE_SECRET', 'test-secret')
        data_json = json.dumps(report, sort_keys=True, ensure_ascii=False)
        signature = hmac.new(
            secret.encode('utf-8'),
            data_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        report["signature"] = signature
        return report
    
    @override_settings(COMPLIANCE_SIGNATURE_SECRET='test-secret')
    @patch('core.api.public_compliance.COMPLIANCE_SIGNATURE_SECRET', 'test-secret')
    @patch('core.api.public_compliance._load_compliance_report')
    def test_constitution_status_compliant(self, mock_load):
        """Test que l'endpoint renvoie 'compliant' pour un rapport valide"""
        report = self._create_valid_report(age_hours=0)
        mock_load.return_value = report
        
        response = self.client.get(self.json_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'compliant')
        self.assertIn('checks', data)
        self.assertIn('proof_hash', data)
    
    @override_settings(COMPLIANCE_SIGNATURE_SECRET='test-secret')
    @patch('core.api.public_compliance.COMPLIANCE_SIGNATURE_SECRET', 'test-secret')
    @patch('core.api.public_compliance._load_compliance_report')
    def test_constitution_status_old_report(self, mock_load):
        """Test que l'endpoint ne renvoie JAMAIS 'compliant' pour un rapport > 24h"""
        report = self._create_valid_report(age_hours=25)  # > 24h
        mock_load.return_value = report
        
        response = self.client.get(self.json_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Ne doit JAMAIS être 'compliant' si > 24h
        self.assertNotEqual(data['status'], 'compliant')
        self.assertEqual(data['status'], 'unknown')
        self.assertIn('error', data)
    
    @override_settings(COMPLIANCE_SIGNATURE_SECRET='test-secret')
    @patch('core.api.public_compliance.COMPLIANCE_SIGNATURE_SECRET', 'test-secret')
    @patch('core.api.public_compliance._load_compliance_report')
    def test_constitution_status_invalid_signature(self, mock_load):
        """Test que l'endpoint ne renvoie JAMAIS 'compliant' pour une signature invalide"""
        report = self._create_valid_report(age_hours=0)
        report['signature'] = 'invalid-signature'  # Signature invalide
        mock_load.return_value = report
        
        response = self.client.get(self.json_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Ne doit JAMAIS être 'compliant' si signature invalide
        self.assertNotEqual(data['status'], 'compliant')
        self.assertEqual(data['status'], 'unknown')
    
    @override_settings(COMPLIANCE_SIGNATURE_SECRET='test-secret')
    @patch('core.api.public_compliance._load_compliance_report')
    def test_constitution_status_missing_report(self, mock_load):
        """Test que l'endpoint renvoie 'unknown' si le rapport est absent"""
        mock_load.return_value = None
        
        response = self.client.get(self.json_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'unknown')
        self.assertIn('error', data)
    
    @override_settings(COMPLIANCE_SIGNATURE_SECRET='test-secret')
    @patch('core.api.public_compliance.COMPLIANCE_SIGNATURE_SECRET', 'test-secret')
    @patch('core.api.public_compliance._load_compliance_report')
    def test_constitution_badge_compliant(self, mock_load):
        """Test que le badge SVG est vert pour 'compliant'"""
        report = self._create_valid_report(age_hours=0)
        mock_load.return_value = report
        
        response = self.client.get(self.svg_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml; charset=utf-8')
        self.assertIn(b'Compliant', response.content)
        self.assertIn(b'#28a745', response.content)  # Vert
    
    @override_settings(COMPLIANCE_SIGNATURE_SECRET='test-secret')
    @patch('core.api.public_compliance._load_compliance_report')
    def test_constitution_badge_unknown(self, mock_load):
        """Test que le badge SVG est orange pour 'unknown'"""
        mock_load.return_value = None
        
        response = self.client.get(self.svg_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml; charset=utf-8')
        self.assertIn(b'Unknown', response.content)
        self.assertIn(b'#ffc107', response.content)  # Orange

