"""
Tests unitaires pour l'endpoint public /api/public/egoejo-compliance-badge.svg

Vérifie que l'endpoint :
- Génère un SVG dynamiquement selon le statut
- Affiche 3 états visuels distincts
- N'utilise aucun asset externe
- Est compatible README GitHub
"""
import re
from django.test import TestCase, Client
from django.core.cache import cache
from unittest.mock import patch
from xml.etree import ElementTree as ET


class EGOEJOComplianceBadgeViewTest(TestCase):
    """
    Tests pour l'endpoint /api/public/egoejo-compliance-badge.svg
    """
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.url = "/api/public/egoejo-compliance-badge.svg"
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
        self.assertEqual(response['Content-Type'], 'image/svg+xml; charset=utf-8')
    
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
    
    def test_svg_valide(self):
        """
        Vérifie que la réponse est un SVG valide.
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        svg_content = response.content.decode('utf-8')
        
        # Vérifier que c'est un SVG
        self.assertIn('<svg', svg_content)
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', svg_content)
        
        # Essayer de parser le SVG
        try:
            ET.fromstring(svg_content)
        except ET.ParseError as e:
            self.fail(f"Le SVG n'est pas valide: {e}")
    
    def test_etat_core_visuel_distinct(self):
        """
        Vérifie que l'état "core" a un visuel distinct.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            response = self.client.get(self.url)
            svg_content = response.content.decode('utf-8')
            
            # Vérifier les couleurs spécifiques à "core"
            self.assertIn('#1a5f3f', svg_content)  # Vert foncé
            self.assertIn('#2d8659', svg_content)  # Vert moyen
            self.assertIn('CORE', svg_content)
            self.assertIn('EGOEJO COMPLIANT', svg_content)
    
    def test_etat_extended_visuel_distinct(self):
        """
        Vérifie que l'état "extended" a un visuel distinct.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-extended"):
            response = self.client.get(self.url)
            svg_content = response.content.decode('utf-8')
            
            # Vérifier les couleurs spécifiques à "extended"
            self.assertIn('#0d4f2d', svg_content)  # Vert très foncé
            self.assertIn('#1a7a4a', svg_content)  # Vert moyen
            self.assertIn('EXTENDED', svg_content)
            self.assertIn('EGOEJO COMPLIANT', svg_content)
    
    def test_etat_non_compliant_visuel_distinct(self):
        """
        Vérifie que l'état "non-compliant" a un visuel distinct.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="non-compliant"):
            response = self.client.get(self.url)
            svg_content = response.content.decode('utf-8')
            
            # Vérifier les couleurs spécifiques à "non-compliant"
            self.assertIn('#6b7280', svg_content)  # Gris foncé
            self.assertIn('#9ca3af', svg_content)  # Gris moyen
            self.assertIn('NON', svg_content)
            self.assertIn('EGOEJO COMPLIANT', svg_content)
    
    def test_aucun_asset_externe(self):
        """
        Vérifie qu'aucun asset externe n'est référencé dans le SVG.
        """
        response = self.client.get(self.url)
        svg_content = response.content.decode('utf-8')
        
        # Vérifier qu'il n'y a pas de références externes (sauf xmlns qui est nécessaire)
        # Pas d'URLs http/https (sauf dans xmlns qui est standard)
        # On vérifie qu'il n'y a pas d'URLs dans href ou autres attributs
        lines = svg_content.split('\n')
        for line in lines:
            # Ignorer la ligne xmlns qui contient nécessairement "http://"
            if 'xmlns=' in line:
                continue
            # Vérifier qu'il n'y a pas d'autres URLs
            if 'http://' in line or 'https://' in line:
                self.fail(f"URL externe détectée dans le SVG: {line}")
        
        # Pas de références à des fichiers externes
        self.assertNotIn('href=', svg_content.lower())
        self.assertNotIn('xlink:href=', svg_content.lower())
        
        # Pas de références à des images externes
        self.assertNotIn('<image', svg_content.lower())
        
        # Tout doit être embarqué (gradients, styles, etc.)
        self.assertIn('<defs>', svg_content)  # Définitions embarquées
        self.assertIn('linearGradient', svg_content)  # Gradient embarqué
    
    def test_compatible_github_readme(self):
        """
        Vérifie que le badge est compatible avec GitHub README.
        """
        response = self.client.get(self.url)
        svg_content = response.content.decode('utf-8')
        
        # Parser le SVG pour vérifier les dimensions
        try:
            root = ET.fromstring(svg_content)
            
            # Vérifier les attributs width et height
            width = root.get('width')
            height = root.get('height')
            
            self.assertIsNotNone(width)
            self.assertIsNotNone(height)
            
            # Dimensions compatibles GitHub (standard: ~150-200px de large, ~20-30px de haut)
            width_int = int(re.sub(r'[^\d]', '', width))
            height_int = int(re.sub(r'[^\d]', '', height))
            
            # Largeur raisonnable pour GitHub README
            self.assertGreaterEqual(width_int, 100)
            self.assertLessEqual(width_int, 300)
            
            # Hauteur raisonnable pour GitHub README
            self.assertGreaterEqual(height_int, 15)
            self.assertLessEqual(height_int, 50)
            
            # Vérifier que viewBox est présent (important pour le scaling)
            viewbox = root.get('viewBox')
            self.assertIsNotNone(viewbox)
            
        except ET.ParseError as e:
            self.fail(f"Impossible de parser le SVG: {e}")
    
    def test_svg_contient_texte_egoejo_compliant(self):
        """
        Vérifie que le SVG contient le texte "EGOEJO COMPLIANT".
        """
        response = self.client.get(self.url)
        svg_content = response.content.decode('utf-8')
        
        self.assertIn('EGOEJO COMPLIANT', svg_content)
    
    def test_svg_contient_texte_saka_eur(self):
        """
        Vérifie que le SVG contient le texte "SAKA ≠ EUR".
        """
        response = self.client.get(self.url)
        svg_content = response.content.decode('utf-8')
        
        self.assertIn('SAKA ≠ EUR', svg_content)
    
    def test_cache_controle(self):
        """
        Vérifie que le cache est correctement utilisé.
        """
        with patch('core.api.compliance_views._determine_compliance_status', return_value="egoejo-compliant-core"):
            # Premier appel
            response1 = self.client.get(self.url)
            self.assertEqual(response1.status_code, 200)
            
            # Vérifier que les en-têtes de cache sont présents
            self.assertIn('Cache-Control', response1)
            self.assertIn('public, max-age=900', response1['Cache-Control'])
            
            # Deuxième appel (devrait utiliser le cache)
            response2 = self.client.get(self.url)
            self.assertEqual(response2.status_code, 200)
            
            # Les contenus doivent être identiques
            self.assertEqual(response1.content, response2.content)
    
    def test_trois_etats_visuels_differents(self):
        """
        Vérifie que les 3 états ont des visuels différents.
        """
        states = [
            ("egoejo-compliant-core", "core"),
            ("egoejo-compliant-extended", "extended"),
            ("non-compliant", "non-compliant")
        ]
        
        svg_contents = []
        
        for status_raw, status_normalized in states:
            with patch('core.api.compliance_views._determine_compliance_status', return_value=status_raw):
                cache.clear()  # Vider le cache pour chaque état
                response = self.client.get(self.url)
                svg_content = response.content.decode('utf-8')
                svg_contents.append((status_normalized, svg_content))
        
        # Vérifier que chaque état a un contenu différent
        for i, (status1, svg1) in enumerate(svg_contents):
            for j, (status2, svg2) in enumerate(svg_contents):
                if i != j:
                    # Les SVG doivent être différents (couleurs, textes)
                    self.assertNotEqual(svg1, svg2, 
                                      f"Les états {status1} et {status2} ont le même SVG")
    
    def test_response_content_type_svg(self):
        """
        Vérifie que le Content-Type est image/svg+xml.
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/svg+xml', response['Content-Type'])
        self.assertIn('charset=utf-8', response['Content-Type'])

