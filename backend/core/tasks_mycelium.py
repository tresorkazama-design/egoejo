"""
Tâches Celery pour réduction de dimensionnalité (Mycélium Numérique)
Transforme les embeddings haute dimension en coordonnées 3D (x, y, z)
"""
from celery import shared_task
import logging
import numpy as np

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def reduce_embeddings_to_3d(self, content_type='both', method='umap'):
    """
    Réduit les embeddings haute dimension en coordonnées 3D pour visualisation.
    
    Args:
        content_type: 'projet', 'educational_content', ou 'both'
        method: 'umap' ou 'tsne'
    
    Returns:
        dict: Résultat de la réduction avec coordonnées 3D
    """
    try:
        if method == 'umap':
            return _reduce_with_umap(content_type)
        elif method == 'tsne':
            return _reduce_with_tsne(content_type)
        else:
            logger.error(f"Méthode de réduction inconnue: {method}")
            return {'success': False, 'error': f'Méthode inconnue: {method}'}
    
    except Exception as exc:
        logger.error(f"Erreur réduction dimensionnalité: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def _reduce_with_umap(content_type):
    """
    Réduction de dimensionnalité avec UMAP.
    Note: UMAP peut ne pas être disponible sur Python 3.14+, fallback sur t-SNE.
    """
    try:
        import umap
        
        # Récupérer les embeddings
        embeddings_data = _get_embeddings_data(content_type)
        if not embeddings_data:
            return {'success': False, 'error': 'Aucun embedding trouvé'}
        
        embeddings = embeddings_data['vectors']
        ids = embeddings_data['ids']
        types = embeddings_data['types']
        
        # Réduire à 3 dimensions
        reducer = umap.UMAP(n_components=3, random_state=42, n_neighbors=15, min_dist=0.1)
        coordinates_3d = reducer.fit_transform(embeddings)
        
        # Sauvegarder les coordonnées dans les modèles
        _save_coordinates_3d(ids, types, coordinates_3d)
        
        logger.info(f"Réduction UMAP réussie pour {len(ids)} éléments")
        return {
            'success': True,
            'count': len(ids),
            'method': 'umap',
            'content_type': content_type
        }
    
    except ImportError:
        logger.warning("umap-learn non installé, fallback sur t-SNE")
        return _reduce_with_tsne(content_type)
    except Exception as exc:
        logger.error(f"Erreur réduction UMAP: {exc}")
        return {'success': False, 'error': str(exc)}


def _reduce_with_tsne(content_type):
    """
    Réduction de dimensionnalité avec t-SNE.
    """
    try:
        from sklearn.manifold import TSNE
        
        # Récupérer les embeddings
        embeddings_data = _get_embeddings_data(content_type)
        if not embeddings_data:
            return {'success': False, 'error': 'Aucun embedding trouvé'}
        
        embeddings = embeddings_data['vectors']
        ids = embeddings_data['ids']
        types = embeddings_data['types']
        
        # Réduire à 3 dimensions
        reducer = TSNE(n_components=3, random_state=42, perplexity=30)
        coordinates_3d = reducer.fit_transform(embeddings)
        
        # Sauvegarder les coordonnées dans les modèles
        _save_coordinates_3d(ids, types, coordinates_3d)
        
        logger.info(f"Réduction t-SNE réussie pour {len(ids)} éléments")
        return {
            'success': True,
            'count': len(ids),
            'method': 'tsne',
            'content_type': content_type
        }
    
    except ImportError:
        logger.error("scikit-learn non installé")
        return {'success': False, 'error': 'scikit-learn not installed'}
    except Exception as exc:
        logger.error(f"Erreur réduction t-SNE: {exc}")
        return {'success': False, 'error': str(exc)}


def _get_embeddings_data(content_type):
    """
    Récupère les embeddings depuis la base de données.
    """
    embeddings = []
    ids = []
    types = []
    
    if content_type in ('projet', 'both'):
        from core.models.projects import Projet
        projets = Projet.objects.filter(embedding__isnull=False)
        for projet in projets:
            if projet.embedding and isinstance(projet.embedding, dict):
                vector = projet.embedding.get('vector')
                if vector and len(vector) > 0:
                    embeddings.append(vector)
                    ids.append(projet.id)
                    types.append('projet')
    
    if content_type in ('educational_content', 'both'):
        from core.models.content import EducationalContent
        contenus = EducationalContent.objects.filter(
            embedding__isnull=False,
            status='published'
        )
        for contenu in contenus:
            if contenu.embedding and isinstance(contenu.embedding, dict):
                vector = contenu.embedding.get('vector')
                if vector and len(vector) > 0:
                    embeddings.append(vector)
                    ids.append(contenu.id)
                    types.append('educational_content')
    
    if not embeddings:
        return None
    
    # Normaliser les longueurs de vecteurs (padding ou troncature)
    max_dim = max(len(v) for v in embeddings)
    embeddings_normalized = []
    for v in embeddings:
        if len(v) < max_dim:
            # Padding avec zéros
            v_padded = list(v) + [0.0] * (max_dim - len(v))
        else:
            # Troncature
            v_padded = v[:max_dim]
        embeddings_normalized.append(v_padded)
    
    return {
        'vectors': np.array(embeddings_normalized),
        'ids': ids,
        'types': types
    }


def _save_coordinates_3d(ids, types, coordinates_3d):
    """
    Sauvegarde les coordonnées 3D dans les modèles.
    """
    for i, (obj_id, obj_type) in enumerate(zip(ids, types)):
        coords = {
            'x': float(coordinates_3d[i][0]),
            'y': float(coordinates_3d[i][1]),
            'z': float(coordinates_3d[i][2])
        }
        
        if obj_type == 'projet':
            from core.models.projects import Projet
            try:
                projet = Projet.objects.get(id=obj_id)
                if not projet.embedding:
                    projet.embedding = {}
                projet.embedding['coordinates_3d'] = coords
                projet.save(update_fields=['embedding'])
            except Projet.DoesNotExist:
                logger.warning(f"Projet {obj_id} non trouvé")
        
        elif obj_type == 'educational_content':
            from core.models.content import EducationalContent
            try:
                contenu = EducationalContent.objects.get(id=obj_id)
                if not contenu.embedding:
                    contenu.embedding = {}
                contenu.embedding['coordinates_3d'] = coords
                contenu.save(update_fields=['embedding'])
            except EducationalContent.DoesNotExist:
                logger.warning(f"Contenu {obj_id} non trouvé")


@shared_task
def batch_reduce_embeddings(method='umap', content_type='both'):
    """
    Lance la réduction de dimensionnalité pour tous les contenus avec embeddings.
    """
    return reduce_embeddings_to_3d.delay(content_type, method)

