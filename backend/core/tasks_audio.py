"""
Tâches Celery pour génération audio (Text-to-Speech)
Génère des versions audio des contenus éducatifs pour accessibilité terrain
"""
from celery import shared_task
import logging
import os

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_audio_content(self, content_id, provider='openai', voice='alloy'):
    """
    Génère un fichier audio (MP3) à partir d'un contenu éducatif.
    
    Args:
        content_id: ID du EducationalContent
        provider: 'openai' ou 'elevenlabs'
        voice: Voix à utiliser (ex: 'alloy', 'echo' pour OpenAI)
    
    Returns:
        dict: Résultat de la génération
    """
    try:
        from core.models.content import EducationalContent
        
        try:
            content = EducationalContent.objects.get(id=content_id)
        except EducationalContent.DoesNotExist:
            logger.error(f"Contenu {content_id} non trouvé")
            return {'success': False, 'error': f'Contenu {content_id} non trouvé'}
        
        # Préparer le texte à convertir
        text = _prepare_text_for_tts(content)
        if not text or len(text.strip()) < 10:
            logger.warning(f"Texte trop court pour TTS: {content_id}")
            return {'success': False, 'error': 'Texte trop court'}

        # Hash du texte pour éviter de payer deux fois
        current_hash = content.compute_text_hash()
        if content.audio_source_hash and content.audio_source_hash == current_hash:
            logger.info(f"Aucun changement détecté, TTS déjà à jour pour contenu {content_id}")
            return {
                'success': True,
                'skipped': True,
                'reason': 'hash_unchanged',
                'content_id': content_id,
            }
        
        # Générer l'audio selon le provider
        if provider == 'openai':
            audio_data = _generate_with_openai(text, voice)
        elif provider == 'elevenlabs':
            audio_data = _generate_with_elevenlabs(text, voice)
        else:
            return {'success': False, 'error': f'Provider inconnu: {provider}'}
        
        if not audio_data:
            return {'success': False, 'error': 'Génération audio échouée'}
        
        # Sauvegarder le fichier audio
        audio_file_path = _save_audio_file(content, audio_data, provider)
        
        # Mettre à jour le modèle (audio + hash)
        content.audio_file = audio_file_path
        content.audio_source_hash = current_hash
        content.save(update_fields=['audio_file', 'audio_source_hash'])
        
        logger.info(f"Audio généré avec succès pour contenu {content_id}")
        return {
            'success': True,
            'content_id': content_id,
            'audio_file': audio_file_path,
            'provider': provider
        }
    
    except Exception as exc:
        logger.error(f"Erreur génération audio pour {content_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def _prepare_text_for_tts(content):
    """
    Prépare le texte du contenu pour TTS.
    """
    text_parts = []
    
    # Titre
    if content.title:
        text_parts.append(f"Titre: {content.title}")
    
    # Description
    if content.description:
        text_parts.append(content.description)
    
    # Si c'est un article, on pourrait extraire le contenu du fichier PDF
    # Pour l'instant, on se contente du titre et de la description
    
    return "\n\n".join(text_parts)


def _generate_with_openai(text, voice='alloy'):
    """
    Génère l'audio avec OpenAI TTS.
    """
    try:
        import openai
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY non configuré")
            return None
        
        openai.api_key = api_key
        
        # Limiter la longueur du texte (OpenAI TTS a des limites)
        max_chars = 4000  # Limite OpenAI TTS
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        # Générer l'audio
        response = openai.audio.speech.create(
            model="tts-1",  # ou "tts-1-hd" pour meilleure qualité
            voice=voice,  # 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'
            input=text
        )
        
        # Retourner les données binaires
        return response.content
    
    except ImportError:
        logger.error("openai non installé")
        return None
    except Exception as exc:
        logger.error(f"Erreur génération OpenAI TTS: {exc}")
        return None


def _generate_with_elevenlabs(text, voice_id='default'):
    """
    Génère l'audio avec ElevenLabs TTS.
    """
    try:
        import requests
        
        api_key = os.environ.get('ELEVENLABS_API_KEY')
        if not api_key:
            logger.warning("ELEVENLABS_API_KEY non configuré")
            return None
        
        # Limiter la longueur du texte
        max_chars = 5000  # Limite ElevenLabs
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        # Appel API ElevenLabs
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)  # nosec B113 - Timeout ajouté
        response.raise_for_status()
        
        return response.content
    
    except ImportError:
        logger.error("requests non installé")
        return None
    except Exception as exc:
        logger.error(f"Erreur génération ElevenLabs TTS: {exc}")
        return None


def _save_audio_file(content, audio_data, provider):
    """
    Sauvegarde le fichier audio sur le storage (R2/S3 ou local).
    """
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage
    
    # Nom du fichier
    filename = f"audio_{content.id}_{provider}.mp3"
    file_path = f"educational_contents/audio/{filename}"
    
    # Sauvegarder via le storage
    saved_path = default_storage.save(file_path, ContentFile(audio_data))
    
    return saved_path


@shared_task
def batch_generate_audio(provider='openai', voice='alloy'):
    """
    Génère les audios pour tous les contenus publiés sans audio.
    """
    from core.models.content import EducationalContent
    
    contenus = EducationalContent.objects.filter(
        status='published',
        audio_file__isnull=True
    )
    
    count = 0
    for contenu in contenus:
        generate_audio_content.delay(contenu.id, provider, voice)
        count += 1
    
    logger.info(f"Génération audio lancée pour {count} contenus")
    return {'success': True, 'count': count}

