"""
EGOEJO Compliance Test : Protection des Endpoints API

LOI EGOEJO :
"Aucun endpoint API ne peut permettre la conversion SAKA ↔ EUR."

Ce test vérifie que :
- Aucun endpoint ne contient "convert", "exchange", "rate" dans son nom
- Aucun endpoint ne retourne un taux de conversion
- Aucun endpoint ne permet de convertir SAKA en EUR ou vice versa

Violation du Manifeste EGOEJO si :
- Un endpoint API permet la conversion SAKA ↔ EUR
- Un endpoint retourne un taux de conversion
- Un endpoint permet d'échanger SAKA contre EUR
"""
import pytest
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
import re


@pytest.mark.egoejo_compliance
class TestAPIEndpointsProtection:
    """
    Tests de conformité : Protection des Endpoints API
    
    RÈGLE ABSOLUE : Aucun endpoint API ne peut permettre la conversion SAKA ↔ EUR.
    """
    
    def _collect_url_patterns(self, resolver, prefix=''):
        """
        Collecte récursivement tous les patterns d'URL.
        
        Args:
            resolver: URLResolver Django
            prefix: Préfixe actuel (pour les URLs imbriquées)
        
        Returns:
            list: Liste de tuples (pattern, view)
        """
        patterns = []
        
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLResolver):
                # URL imbriquée, récursion
                new_prefix = prefix + str(pattern.pattern)
                patterns.extend(self._collect_url_patterns(pattern, new_prefix))
            elif isinstance(pattern, URLPattern):
                # Pattern final
                full_pattern = prefix + str(pattern.pattern)
                patterns.append((full_pattern, pattern.callback))
        
        return patterns
    
    def test_aucun_endpoint_conversion_detecte(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un endpoint API contient "convert", "exchange", ou "rate" dans son nom.
        
        Test : Scan tous les endpoints API pour détecter les patterns interdits.
        """
        resolver = get_resolver()
        patterns = self._collect_url_patterns(resolver)
        
        # Patterns interdits (mots-clés suspects)
        forbidden_keywords = [
            'convert',
            'exchange',
            'rate',
            'saka.*eur',
            'eur.*saka',
        ]
        
        violations = []
        
        for pattern_str, view in patterns:
            pattern_lower = pattern_str.lower()
            
            # Vérifier les mots-clés interdits
            for keyword in forbidden_keywords:
                if re.search(keyword, pattern_lower, re.IGNORECASE):
                    # Vérifier que ce n'est pas un endpoint autorisé (ex: "rate_limiting")
                    if 'rate_limiting' not in pattern_lower:
                        violations.append((pattern_str, keyword))
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"Endpoints suspects détectés : {violations}. "
            f"Aucun endpoint API ne peut permettre la conversion SAKA ↔ EUR."
        )
    
    def test_aucun_endpoint_saka_conversion(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un endpoint SAKA permet la conversion.
        
        Test : Vérifier spécifiquement les endpoints SAKA.
        """
        resolver = get_resolver()
        patterns = self._collect_url_patterns(resolver)
        
        # Filtrer les endpoints SAKA
        saka_patterns = [
            (pattern, view) for pattern, view in patterns
            if 'saka' in pattern.lower()
        ]
        
        # Patterns interdits pour endpoints SAKA
        forbidden_patterns = [
            r'convert',
            r'exchange',
            r'rate.*eur',
            r'eur.*rate',
        ]
        
        violations = []
        
        for pattern_str, view in saka_patterns:
            for forbidden in forbidden_patterns:
                if re.search(forbidden, pattern_str, re.IGNORECASE):
                    violations.append((pattern_str, forbidden))
        
        assert len(violations) == 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"Endpoints SAKA suspects détectés : {violations}. "
            f"Aucun endpoint SAKA ne peut permettre la conversion."
        )
    
    def test_endpoints_saka_autorises(self):
        """
        Vérifie que les endpoints SAKA autorisés existent.
        
        Endpoints autorisés :
        - /api/saka/balance/ (lecture solde)
        - /api/saka/harvest/ (récolte)
        - /api/saka/spend/ (dépense)
        - /api/saka/boost/ (boost projet)
        """
        resolver = get_resolver()
        patterns = self._collect_url_patterns(resolver)
        
        # Endpoints SAKA autorisés (patterns flexibles)
        authorized_patterns = [
            r'saka.*balance',
            r'saka.*harvest',
            r'saka.*spend',
            r'saka.*boost',
            r'saka.*info',
            r'saka.*wallet',
        ]
        
        found_patterns = []
        
        for pattern_str, view in patterns:
            for authorized in authorized_patterns:
                if re.search(authorized, pattern_str, re.IGNORECASE):
                    found_patterns.append(pattern_str)
        
        # Au moins un endpoint SAKA doit exister OU SAKA peut être désactivé
        # (si ENABLE_SAKA=False, les endpoints peuvent ne pas exister)
        from django.conf import settings
        saka_enabled = getattr(settings, 'ENABLE_SAKA', False)
        
        if saka_enabled:
            assert len(found_patterns) > 0, (
                "Aucun endpoint SAKA autorisé trouvé alors que SAKA est activé. "
                "Vérifier que les endpoints SAKA sont correctement configurés."
            )
        else:
            # Si SAKA est désactivé, c'est acceptable qu'il n'y ait pas d'endpoints
            pass
    
    def test_scan_complet_endpoints_et_serializers(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un endpoint ou son serializer suggère conversion, achat, valeur financière, accumulation.
        
        Test : Scanner automatiquement toutes les routes Django (APIView, ViewSet) et leurs serializers.
        
        Vérifie :
        - Noms de routes
        - Serializers liés
        - Noms de méthodes/actions
        - Champs des serializers
        
        Le test FAIL si un seul pattern est trouvé.
        """
        from django.urls import get_resolver
        from django.urls.resolvers import URLPattern, URLResolver
        from rest_framework.viewsets import ViewSet
        from rest_framework.views import APIView
        from rest_framework import generics
        import inspect
        
        resolver = get_resolver()
        patterns = self._collect_url_patterns(resolver)
        
        # Patterns interdits explicites
        FORBIDDEN_PATTERNS = [
            # Conversion
            (r'convert', 'Conversion monétaire'),
            (r'exchange', 'Échange monétaire'),
            (r'rate.*(?:eur|usd|gbp|currency)', 'Taux de change'),
            (r'(?:eur|usd|gbp|currency).*rate', 'Taux de change'),
            (r'saka.*to.*(?:eur|usd|gbp|currency)', 'Conversion SAKA vers devise'),
            (r'(?:eur|usd|gbp|currency).*to.*saka', 'Conversion devise vers SAKA'),
            
            # Achat/Vente
            (r'buy', 'Achat'),
            (r'purchase', 'Achat'),
            (r'sell', 'Vente'),
            (r'trade', 'Échange commercial'),
            (r'market', 'Marché'),
            (r'order', 'Commande commerciale'),
            
            # Valeur financière
            (r'price', 'Prix'),
            (r'cost', 'Coût'),
            (r'value.*(?:eur|usd|gbp|currency)', 'Valeur monétaire'),
            (r'worth.*(?:eur|usd|gbp|currency)', 'Valeur monétaire (worth)'),
            (r'equivalent.*(?:eur|usd|gbp|currency)', 'Équivalent monétaire'),
            (r'(?:eur|usd|gbp|currency).*equivalent', 'Équivalent monétaire'),
            
            # Accumulation
            (r'accumulate', 'Accumulation'),
            (r'interest', 'Intérêt'),
            (r'yield', 'Rendement'),
            (r'profit', 'Profit'),
            (r'dividend', 'Dividende'),
            (r'investment', 'Investissement'),
            (r'speculation', 'Spéculation'),
            (r'return.*rate', 'Taux de rendement'),
        ]
        
        # Compiler les patterns
        compiled_patterns = []
        for pattern_str, description in FORBIDDEN_PATTERNS:
            try:
                compiled_patterns.append((re.compile(pattern_str, re.IGNORECASE), description))
            except re.error as e:
                pytest.fail(f"Pattern regex invalide : {pattern_str} - {e}")
        
        all_violations = []
        
        # Scanner toutes les routes
        for pattern_str, view in patterns:
            # Ignorer les routes non-API (pas dans /api/)
            if '/api/' not in pattern_str:
                continue
            
            violations_for_endpoint = []
            
            # 1. Scanner le nom de la route
            pattern_lower = pattern_str.lower()
            for compiled_pattern, description in compiled_patterns:
                if compiled_pattern.search(pattern_lower):
                    # Exceptions autorisées
                    if 'rate_limiting' in pattern_lower:
                        continue
                    violations_for_endpoint.append({
                        'type': 'route_name',
                        'pattern': description,
                        'match': compiled_pattern.search(pattern_lower).group(),
                        'location': pattern_str
                    })
            
            # 2. Scanner la vue et son serializer
            try:
                # Obtenir la classe de la vue
                view_class = None
                if hasattr(view, 'view_class'):
                    view_class = view.view_class
                elif inspect.isclass(view):
                    view_class = view
                elif hasattr(view, '__class__'):
                    # Vue fonction ou callable
                    view_class = view.__class__
                else:
                    # Vue fonction, ignorer pour le moment
                    view_class = None
                
                if view_class and inspect.isclass(view_class):
                    # Vérifier le nom de la classe
                    class_name = view_class.__name__.lower()
                    for compiled_pattern, description in compiled_patterns:
                        if compiled_pattern.search(class_name):
                            violations_for_endpoint.append({
                                'type': 'view_class',
                                'pattern': description,
                                'match': compiled_pattern.search(class_name).group(),
                                'location': f"{view_class.__module__}.{view_class.__name__}"
                            })
                    
                    # Vérifier le serializer
                    serializer_class = None
                    if hasattr(view_class, 'serializer_class'):
                        serializer_class = view_class.serializer_class
                    elif hasattr(view_class, 'get_serializer_class'):
                        try:
                            serializer_class = view_class.get_serializer_class()
                        except:
                            pass
                    
                    if serializer_class:
                        serializer_name = serializer_class.__name__.lower()
                        for compiled_pattern, description in compiled_patterns:
                            if compiled_pattern.search(serializer_name):
                                violations_for_endpoint.append({
                                    'type': 'serializer_class',
                                    'pattern': description,
                                    'match': compiled_pattern.search(serializer_name).group(),
                                    'location': f"{serializer_class.__module__}.{serializer_class.__name__}"
                                })
                        
                        # Scanner les champs du serializer
                        if hasattr(serializer_class, 'Meta') and hasattr(serializer_class.Meta, 'fields'):
                            fields = serializer_class.Meta.fields
                            if isinstance(fields, (list, tuple)):
                                for field in fields:
                                    field_lower = str(field).lower()
                                    for compiled_pattern, description in compiled_patterns:
                                        if compiled_pattern.search(field_lower):
                                            violations_for_endpoint.append({
                                                'type': 'serializer_field',
                                                'pattern': description,
                                                'match': compiled_pattern.search(field_lower).group(),
                                                'location': f"{serializer_class.__name__}.Meta.fields['{field}']"
                                            })
                        
                        # Scanner les champs déclarés explicitement
                        for attr_name in dir(serializer_class):
                            if not attr_name.startswith('_') and attr_name not in ['Meta', 'serializer_class']:
                                attr_lower = attr_name.lower()
                                for compiled_pattern, description in compiled_patterns:
                                    if compiled_pattern.search(attr_lower):
                                        violations_for_endpoint.append({
                                            'type': 'serializer_attribute',
                                            'pattern': description,
                                            'match': compiled_pattern.search(attr_lower).group(),
                                            'location': f"{serializer_class.__name__}.{attr_name}"
                                        })
                    
                    # Vérifier les actions personnalisées (ViewSet)
                    if view_class and (issubclass(view_class, ViewSet) if inspect.isclass(view_class) else False):
                        for attr_name in dir(view_class):
                            if not attr_name.startswith('_'):
                                try:
                                    attr = getattr(view_class, attr_name)
                                    if callable(attr) and hasattr(attr, 'url_path'):
                                        # C'est une action décorée avec @action
                                        action_name = attr_name.lower()
                                        for compiled_pattern, description in compiled_patterns:
                                            if compiled_pattern.search(action_name):
                                                violations_for_endpoint.append({
                                                    'type': 'viewset_action',
                                                    'pattern': description,
                                                    'match': compiled_pattern.search(action_name).group(),
                                                    'location': f"{view_class.__name__}.{attr_name}()"
                                                })
                                except Exception:
                                    pass
                    
                    # Vérifier les méthodes HTTP personnalisées (APIView)
                    if view_class and (issubclass(view_class, (APIView, generics.GenericAPIView)) if inspect.isclass(view_class) else False):
                        for method_name in ['get', 'post', 'put', 'patch', 'delete']:
                            if hasattr(view_class, method_name):
                                try:
                                    method = getattr(view_class, method_name)
                                    if callable(method):
                                        try:
                                            method_code = inspect.getsource(method)
                                            for compiled_pattern, description in compiled_patterns:
                                                if compiled_pattern.search(method_code.lower()):
                                                    violations_for_endpoint.append({
                                                        'type': 'view_method',
                                                        'pattern': description,
                                                        'match': compiled_pattern.search(method_code.lower()).group(),
                                                        'location': f"{view_class.__name__}.{method_name}()"
                                                    })
                                        except (OSError, TypeError):
                                            # Impossible de récupérer le code source (méthode C, etc.)
                                            pass
                                except Exception:
                                    pass
            
            except Exception as e:
                # Ignorer les erreurs d'inspection (vues complexes, etc.)
                pass
            
            # Ajouter les violations pour cet endpoint
            if violations_for_endpoint:
                all_violations.append({
                    'endpoint': pattern_str,
                    'view': str(view) if view else 'Unknown',
                    'violations': violations_for_endpoint
                })
        
        # Générer le rapport détaillé
        if all_violations:
            report_lines = [
                "=" * 80,
                "VIOLATION DU MANIFESTE EGOEJO : Endpoints interdits détectés",
                "=" * 80,
                "",
                f"Nombre total d'endpoints violants : {len(all_violations)}",
                "",
            ]
            
            for endpoint_data in all_violations:
                report_lines.extend([
                    f"\n🔴 Endpoint : {endpoint_data['endpoint']}",
                    f"   Vue : {endpoint_data['view']}",
                    f"   Violations : {len(endpoint_data['violations'])}",
                    "-" * 80,
                ])
                
                for violation in endpoint_data['violations']:
                    report_lines.extend([
                        f"  ❌ Type : {violation['type']}",
                        f"     Pattern : {violation['pattern']}",
                        f"     Match : {violation['match']}",
                        f"     Localisation : {violation['location']}",
                        "",
                    ])
            
            report_lines.extend([
                "=" * 80,
                "ACTION REQUISE : Supprimer ou corriger tous les endpoints violants.",
                "=" * 80,
            ])
            
            report = "\n".join(report_lines)
            
            pytest.fail(
                f"\n{report}\n\n"
                f"Le test FAIL car {len(all_violations)} endpoint(s) viole(nt) les règles EGOEJO. "
                f"Toute violation doit être corrigée avant de pouvoir continuer."
            )
        
        # Si aucune violation, le test passe
        assert len(all_violations) == 0, "Aucune violation ne devrait être détectée si le test arrive ici."

