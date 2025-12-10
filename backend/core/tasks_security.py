"""
Tâches Celery pour sécurité (scan anti-virus, validation fichiers)
"""
from celery import shared_task
import logging
import os

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def scan_file_antivirus(self, file_path):
    """
    Scanne un fichier uploadé avec ClamAV pour détecter les virus/malware.
    
    Args:
        file_path: Chemin vers le fichier à scanner
    
    Returns:
        dict: Résultat du scan
    """
    try:
        # Vérifier si ClamAV est disponible
        try:
            import pyclamd
        except ImportError:
            logger.warning("pyclamd non installé, scan antivirus ignoré")
            return {
                'success': True,
                'scanned': False,
                'reason': 'ClamAV not installed',
                'safe': True  # Par défaut, considérer comme sûr si ClamAV non disponible
            }
        
        # Se connecter à ClamAV (local ou réseau)
        clamav_host = os.environ.get('CLAMAV_HOST', 'localhost')
        clamav_port = int(os.environ.get('CLAMAV_PORT', 3310))
        
        try:
            cd = pyclamd.ClamdNetworkSocket(host=clamav_host, port=clamav_port)
            cd.ping()
        except Exception:
            # Fallback sur socket Unix si disponible
            try:
                cd = pyclamd.ClamdUnixSocket()
                cd.ping()
            except Exception:
                logger.warning("ClamAV non accessible, scan ignoré")
                return {
                    'success': True,
                    'scanned': False,
                    'reason': 'ClamAV not accessible',
                    'safe': True
                }
        
        # Scanner le fichier
        from django.core.files.storage import default_storage
        
        with default_storage.open(file_path, 'rb') as f:
            scan_result = cd.scan_stream(f.read())
        
        if scan_result is None:
            # Aucun virus détecté
            logger.info(f"Fichier {file_path} scanné et sûr")
            return {
                'success': True,
                'scanned': True,
                'safe': True,
                'file_path': file_path
            }
        else:
            # Virus détecté
            virus_name = list(scan_result.values())[0] if scan_result else 'Unknown'
            logger.warning(f"Virus détecté dans {file_path}: {virus_name}")
            
            # Supprimer le fichier malveillant
            try:
                default_storage.delete(file_path)
            except Exception as e:
                logger.error(f"Erreur suppression fichier malveillant {file_path}: {e}")
            
            return {
                'success': True,
                'scanned': True,
                'safe': False,
                'virus': virus_name,
                'file_path': file_path,
                'deleted': True
            }
    
    except Exception as exc:
        logger.error(f"Erreur scan antivirus pour {file_path}: {exc}")
        # En cas d'erreur, considérer comme sûr pour ne pas bloquer l'utilisateur
        return {
            'success': False,
            'scanned': False,
            'safe': True,
            'error': str(exc)
        }


@shared_task
def validate_file_type(file_path, allowed_types=None):
    """
    Valide le type MIME d'un fichier uploadé.
    
    Args:
        file_path: Chemin vers le fichier
        allowed_types: Liste des types MIME autorisés (ex: ['image/jpeg', 'image/png'])
    
    Returns:
        dict: Résultat de la validation
    """
    try:
        import magic
        
        from django.core.files.storage import default_storage
        
        with default_storage.open(file_path, 'rb') as f:
            file_content = f.read(1024)  # Lire les premiers bytes pour détection
        
        mime = magic.Magic(mime=True)
        detected_type = mime.from_buffer(file_content)
        
        if allowed_types and detected_type not in allowed_types:
            logger.warning(f"Type MIME non autorisé pour {file_path}: {detected_type}")
            return {
                'success': False,
                'valid': False,
                'detected_type': detected_type,
                'allowed_types': allowed_types
            }
        
        logger.info(f"Type MIME validé pour {file_path}: {detected_type}")
        return {
            'success': True,
            'valid': True,
            'detected_type': detected_type
        }
    
    except ImportError:
        logger.warning("python-magic non installé, validation type ignorée")
        return {
            'success': True,
            'valid': True,
            'reason': 'python-magic not installed'
        }
    except Exception as exc:
        logger.error(f"Erreur validation type fichier {file_path}: {exc}")
        return {
            'success': False,
            'valid': False,
            'error': str(exc)
        }

