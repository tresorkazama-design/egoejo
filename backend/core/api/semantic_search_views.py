"""
Endpoints API pour recherche sémantique (embeddings vectoriels)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)


class SemanticSearchView(APIView):
    """
    Endpoint pour recherche sémantique de projets et contenus.
    GET /api/projets/semantic-search/?q=query&type=projet|content|both
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'both')  # 'projet', 'content', 'both'
        
        if not query or len(query) < 2:
            return Response({
                'error': 'Query trop courte (minimum 2 caractères)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Générer embedding de la requête
            query_embedding = self._generate_query_embedding(query)
            if not query_embedding:
                return Response({
                    'error': 'Impossible de générer embedding pour la requête'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            results = {
                'query': query,
                'type': search_type,
                'results': []
            }
            
            # Recherche dans les projets
            if search_type in ('projet', 'both'):
                projets = self._search_projets(query_embedding, query)
                results['results'].extend(projets)
            
            # Recherche dans les contenus éducatifs
            if search_type in ('content', 'both'):
                contenus = self._search_contenus(query_embedding, query)
                results['results'].extend(contenus)
            
            # Trier par similarité
            results['results'].sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return Response(results)
        
        except Exception as exc:
            logger.error(f"Erreur recherche sémantique: {exc}")
            return Response({
                'error': 'Erreur lors de la recherche sémantique'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_query_embedding(self, query):
        """
        Génère un embedding pour la requête utilisateur.
        """
        try:
            import os
            
            # Essayer OpenAI d'abord
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                try:
                    import openai
                    openai.api_key = api_key
                    response = openai.embeddings.create(
                        model="text-embedding-3-small",
                        input=query
                    )
                    return response.data[0].embedding
                except Exception as e:
                    logger.warning(f"Erreur OpenAI embedding: {e}")
            
            # Fallback sur Sentence Transformers
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                return model.encode(query).tolist()
            except ImportError:
                logger.warning("Sentence Transformers non installé")
                return None
        
        except Exception as exc:
            logger.error(f"Erreur génération embedding requête: {exc}")
            return None
    
    def _search_projets(self, query_embedding, query_text):
        """
        Recherche sémantique dans les projets.
        """
        from core.models.projects import Projet
        from django.db.models import Q
        
        results = []
        
        # Recherche textuelle (fallback si pas d'embeddings)
        projets_text = Projet.objects.filter(
            Q(titre__icontains=query_text) | Q(description__icontains=query_text)
        )[:10]
        
        for projet in projets_text:
            similarity = 0.5  # Similarité par défaut pour recherche textuelle
            
            # Calculer similarité vectorielle si embedding disponible
            if projet.embedding and isinstance(projet.embedding, dict):
                projet_vector = projet.embedding.get('vector')
                if projet_vector and len(projet_vector) == len(query_embedding):
                    similarity = self._cosine_similarity(query_embedding, projet_vector)
            
            results.append({
                'type': 'projet',
                'id': projet.id,
                'titre': projet.titre,
                'description': projet.description[:200],
                'similarity': similarity,
                'url': f'/projets/{projet.id}'
            })
        
        return results
    
    def _search_contenus(self, query_embedding, query_text):
        """
        Recherche sémantique dans les contenus éducatifs.
        """
        from core.models.content import EducationalContent
        from django.db.models import Q
        
        results = []
        
        # Recherche textuelle (fallback si pas d'embeddings)
        contenus_text = EducationalContent.objects.filter(
            status='published'
        ).filter(
            Q(title__icontains=query_text) | Q(description__icontains=query_text)
        )[:10]
        
        for contenu in contenus_text:
            similarity = 0.5  # Similarité par défaut pour recherche textuelle
            
            # Calculer similarité vectorielle si embedding disponible
            if contenu.embedding and isinstance(contenu.embedding, dict):
                contenu_vector = contenu.embedding.get('vector')
                if contenu_vector and len(contenu_vector) == len(query_embedding):
                    similarity = self._cosine_similarity(query_embedding, contenu_vector)
            
            results.append({
                'type': 'content',
                'id': contenu.id,
                'title': contenu.title,
                'description': contenu.description[:200] if contenu.description else '',
                'similarity': similarity,
                'url': f'/contenus/{contenu.slug}'
            })
        
        return results
    
    def _cosine_similarity(self, vec1, vec2):
        """
        Calcule la similarité cosinus entre deux vecteurs.
        """
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot_product / (norm1 * norm2))
        except Exception:
            # Fallback simple si numpy non disponible
            if len(vec1) != len(vec2):
                return 0.0
            dot = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)


class SemanticSuggestionsView(APIView):
    """
    Endpoint pour suggestions sémantiques basées sur un projet ou contenu.
    GET /api/projets/semantic-suggestions/?projet_id=123&limit=5
    GET /api/projets/semantic-suggestions/?content_id=456&limit=5
    """
    permission_classes = [AllowAny]

    def get(self, request):
        projet_id = request.query_params.get('projet_id')
        content_id = request.query_params.get('content_id')
        limit = int(request.query_params.get('limit', 5))
        
        if not projet_id and not content_id:
            return Response({
                'error': 'projet_id ou content_id requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            suggestions = []
            
            if projet_id:
                suggestions = self._get_projet_suggestions(projet_id, limit)
            elif content_id:
                suggestions = self._get_content_suggestions(content_id, limit)
            
            return Response({
                'suggestions': suggestions
            })
        
        except Exception as exc:
            logger.error(f"Erreur suggestions sémantiques: {exc}")
            return Response({
                'error': 'Erreur lors de la génération des suggestions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_projet_suggestions(self, projet_id, limit):
        """
        Suggestions de contenus liés à un projet.
        """
        from core.models.projects import Projet
        from core.models.content import EducationalContent
        
        try:
            projet = Projet.objects.get(id=projet_id)
        except Projet.DoesNotExist:
            return []
        
        if not projet.embedding or not isinstance(projet.embedding, dict):
            return []
        
        projet_vector = projet.embedding.get('vector')
        if not projet_vector:
            return []
        
        suggestions = []
        contenus = EducationalContent.objects.filter(
            status='published',
            embedding__isnull=False
        )
        
        for contenu in contenus[:50]:  # Limiter pour performance
            if contenu.embedding and isinstance(contenu.embedding, dict):
                contenu_vector = contenu.embedding.get('vector')
                if contenu_vector and len(contenu_vector) == len(projet_vector):
                    similarity = self._cosine_similarity(projet_vector, contenu_vector)
                    if similarity > 0.3:  # Seuil de similarité
                        suggestions.append({
                            'type': 'content',
                            'id': contenu.id,
                            'title': contenu.title,
                            'similarity': similarity,
                            'url': f'/contenus/{contenu.slug}'
                        })
        
        suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        return suggestions[:limit]
    
    def _get_content_suggestions(self, content_id, limit):
        """
        Suggestions de projets liés à un contenu.
        """
        from core.models.content import EducationalContent
        from core.models.projects import Projet
        
        try:
            contenu = EducationalContent.objects.get(id=content_id)
        except EducationalContent.DoesNotExist:
            return []
        
        if not contenu.embedding or not isinstance(contenu.embedding, dict):
            return []
        
        contenu_vector = contenu.embedding.get('vector')
        if not contenu_vector:
            return []
        
        suggestions = []
        projets = Projet.objects.filter(embedding__isnull=False)
        
        for projet in projets[:50]:  # Limiter pour performance
            if projet.embedding and isinstance(projet.embedding, dict):
                projet_vector = projet.embedding.get('vector')
                if projet_vector and len(projet_vector) == len(contenu_vector):
                    similarity = self._cosine_similarity(contenu_vector, projet_vector)
                    if similarity > 0.3:  # Seuil de similarité
                        suggestions.append({
                            'type': 'projet',
                            'id': projet.id,
                            'titre': projet.titre,
                            'similarity': similarity,
                            'url': f'/projets/{projet.id}'
                        })
        
        suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        return suggestions[:limit]
    
    def _cosine_similarity(self, vec1, vec2):
        """
        Calcule la similarité cosinus entre deux vecteurs.
        """
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot_product / (norm1 * norm2))
        except Exception:
            # Fallback simple si numpy non disponible
            if len(vec1) != len(vec2):
                return 0.0
            dot = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

