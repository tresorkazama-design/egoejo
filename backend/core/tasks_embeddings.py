"""
Tâches Celery pour génération d'embeddings (recherche sémantique)
"""
from celery import shared_task
import logging
import os
import hashlib

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_embedding_task(self, model_name, content_id, content_type='projet'):
    """
    Génère un embedding pour un Projet ou EducationalContent.
    
    Args:
        model_name: Nom du modèle d'embedding ('openai' ou 'sentence-transformers')
        content_id: ID du Projet ou EducationalContent
        content_type: 'projet' ou 'educational_content'
    
    Returns:
        dict: Résultat de la génération
    """
    try:
        if model_name == 'openai':
            return _generate_openai_embedding(content_id, content_type)
        elif model_name == 'sentence-transformers':
            return _generate_sentence_transformers_embedding(content_id, content_type)
        else:
            logger.error(f"Modèle d'embedding inconnu: {model_name}")
            return {'success': False, 'error': f'Modèle inconnu: {model_name}'}
    
    except Exception as exc:
        logger.error(f"Erreur génération embedding pour {content_type} {content_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def _generate_openai_embedding(content_id, content_type):
    """
    Génère un embedding via OpenAI API.
    """
    try:
        import openai
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY non configuré, embedding non généré")
            return {'success': False, 'error': 'OPENAI_API_KEY not configured'}
        
        openai.api_key = api_key
        
        # Récupérer le contenu
        if content_type == 'projet':
            from core.models.projects import Projet
            obj = Projet.objects.get(id=content_id)
            text = f"{obj.titre} {obj.description}"
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        elif content_type == 'educational_content':
            from core.models.content import EducationalContent
            obj = EducationalContent.objects.get(id=content_id)
            text = f"{obj.title} {obj.description}"
            text_hash = obj.compute_text_hash()
            # Skip si hash identique (pas de régénération payante)
            if getattr(obj, "embedding_source_hash", "") == text_hash:
                logger.info(f"Embedding déjà à jour pour content {content_id}, hash identique")
                return {'success': True, 'skipped': True, 'reason': 'hash_unchanged'}
        else:
            return {'success': False, 'error': f'Type inconnu: {content_type}'}
        
        # Générer l'embedding
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        
        embedding = response.data[0].embedding
        
        # Sauvegarder dans le modèle
        obj.embedding = {
            'model': 'text-embedding-3-small',
            'dimension': len(embedding),
            'vector': embedding
        }
        if hasattr(obj, "embedding_source_hash"):
            obj.embedding_source_hash = text_hash
            obj.save(update_fields=['embedding', 'embedding_source_hash'])
        else:
            obj.save()
        
        logger.info(f"Embedding généré pour {content_type} {content_id}")
        return {'success': True, 'content_id': content_id, 'dimension': len(embedding)}
    
    except Exception as exc:
        logger.error(f"Erreur génération OpenAI embedding: {exc}")
        return {'success': False, 'error': str(exc)}


def _generate_sentence_transformers_embedding(content_id, content_type):
    """
    Génère un embedding via Sentence Transformers (local).
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        # Charger le modèle (cache local)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Récupérer le contenu
        if content_type == 'projet':
            from core.models.projects import Projet
            obj = Projet.objects.get(id=content_id)
            text = f"{obj.titre} {obj.description}"
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        elif content_type == 'educational_content':
            from core.models.content import EducationalContent
            obj = EducationalContent.objects.get(id=content_id)
            text = f"{obj.title} {obj.description}"
            text_hash = obj.compute_text_hash()
            if getattr(obj, "embedding_source_hash", "") == text_hash:
                logger.info(f"Embedding déjà à jour (Sentence Transformers) pour content {content_id}")
                return {'success': True, 'skipped': True, 'reason': 'hash_unchanged'}
        else:
            return {'success': False, 'error': f'Type inconnu: {content_type}'}
        
        # Générer l'embedding
        embedding = model.encode(text).tolist()
        
        # Sauvegarder dans le modèle
        obj.embedding = {
            'model': 'all-MiniLM-L6-v2',
            'dimension': len(embedding),
            'vector': embedding
        }
        if hasattr(obj, "embedding_source_hash"):
            obj.embedding_source_hash = text_hash
            obj.save(update_fields=['embedding', 'embedding_source_hash'])
        else:
            obj.save()
        
        logger.info(f"Embedding généré (Sentence Transformers) pour {content_type} {content_id}")
        return {'success': True, 'content_id': content_id, 'dimension': len(embedding)}
    
    except ImportError:
        logger.error("sentence-transformers non installé")
        return {'success': False, 'error': 'sentence-transformers not installed'}
    except Exception as exc:
        logger.error(f"Erreur génération Sentence Transformers embedding: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def batch_generate_embeddings(model_name='sentence-transformers', content_type='projet'):
    """
    Génère les embeddings pour tous les contenus sans embedding.
    
    Args:
        model_name: 'openai' ou 'sentence-transformers'
        content_type: 'projet' ou 'educational_content'
    """
    try:
        if content_type == 'projet':
            from core.models.projects import Projet
            objects = Projet.objects.filter(embedding__isnull=True)
        elif content_type == 'educational_content':
            from core.models.content import EducationalContent
            objects = EducationalContent.objects.filter(embedding__isnull=True)
        else:
            return {'success': False, 'error': f'Type inconnu: {content_type}'}
        
        count = 0
        for obj in objects:
            generate_embedding_task.delay(model_name, obj.id, content_type)
            count += 1
        
        logger.info(f"Génération embeddings lancée pour {count} {content_type}(s)")
        return {'success': True, 'count': count, 'content_type': content_type}
    
    except Exception as exc:
        logger.error(f"Erreur batch génération embeddings: {exc}")
        return {'success': False, 'error': str(exc)}

