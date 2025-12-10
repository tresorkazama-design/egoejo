"""
Tâches asynchrones Celery pour traitement en arrière-plan
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import os
import resend
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def notify_project_success_task(self, project_id):
    """
    Tâche Celery pour notifier les donateurs/investisseurs du succès d'un projet.
    CORRECTION 4 : Asynchronisme pour éviter timeout lors de la clôture.
    
    Args:
        project_id: ID du projet qui a réussi
    """
    try:
        from core.models import Projet
        from finance.models import EscrowContract
        
        project = Projet.objects.get(id=project_id)
        
        # Récupérer tous les escrows libérés pour ce projet
        escrows = EscrowContract.objects.filter(
            project=project,
            status='RELEASED'
        ).select_related('user')
        
        # Envoyer un email à chaque donateur/investisseur
        for escrow in escrows:
            if escrow.user and escrow.user.email:
                subject = f"🎉 Le projet '{project.titre}' a réussi !"
                html_content = f"""
                <h1>Félicitations !</h1>
                <p>Le projet <strong>{project.titre}</strong> a atteint son objectif.</p>
                <p>Votre contribution de <strong>{escrow.amount} €</strong> a été libérée.</p>
                <p>Merci pour votre soutien !</p>
                """
                send_email_task.delay(
                    to_email=escrow.user.email,
                    subject=subject,
                    html_content=html_content
                )
        
        logger.info(f"Notifications envoyées pour le projet {project_id} ({escrows.count()} contributeurs)")
        return {'success': True, 'notified_count': escrows.count()}
    
    except Exception as exc:
        logger.error(f"Erreur notification projet {project_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)  # Réessayer après 60 secondes


@shared_task(bind=True, max_retries=3)
def send_email_task(self, to_email, subject, html_content, text_content=None):
    """
    Envoie un email de manière asynchrone via Resend.
    
    Args:
        to_email: Adresse email destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML
        text_content: Contenu texte (optionnel)
    
    Returns:
        dict: Résultat de l'envoi
    """
    try:
        resend_api_key = os.environ.get('RESEND_API_KEY')
        if not resend_api_key:
            logger.warning("RESEND_API_KEY non configuré, email non envoyé")
            return {'success': False, 'error': 'RESEND_API_KEY not configured'}
        
        resend.api_key = resend_api_key
        
        params = {
            "from": os.environ.get('NOTIFY_EMAIL', 'noreply@egoejo.org'),
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        if text_content:
            params["text"] = text_content
        
        email = resend.Emails.send(params)
        
        logger.info(f"Email envoyé avec succès à {to_email}: {email.get('id')}")
        return {'success': True, 'email_id': email.get('id')}
    
    except Exception as exc:
        logger.error(f"Erreur envoi email à {to_email}: {exc}")
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def update_impact_dashboard_metrics(user_id):
    """
    Met à jour les métriques du tableau de bord d'impact en arrière-plan.
    
    Args:
        user_id: ID de l'utilisateur
    """
    try:
        from core.models.impact import ImpactDashboard
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        dashboard, created = ImpactDashboard.objects.get_or_create(user=user)
        dashboard.update_metrics()
        
        logger.info(f"Métriques ImpactDashboard mises à jour pour user {user_id}")
        return {'success': True, 'user_id': user_id}
    
    except Exception as exc:
        logger.error(f"Erreur mise à jour métriques ImpactDashboard pour user {user_id}: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def process_image_task(image_path, max_width=1920, max_height=1080, quality=85):
    """
    Traite une image uploadée : redimensionnement et optimisation.
    
    Args:
        image_path: Chemin vers l'image à traiter
        max_width: Largeur maximale (défaut: 1920px)
        max_height: Hauteur maximale (défaut: 1080px)
        quality: Qualité JPEG (défaut: 85)
    
    Returns:
        dict: Résultat du traitement
    """
    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Ouvrir l'image
        with default_storage.open(image_path, 'rb') as f:
            image = Image.open(f)
            image_format = image.format or 'JPEG'
            
            # Convertir en RGB si nécessaire (pour JPEG)
            if image_format == 'JPEG' and image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionner si nécessaire
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Sauvegarder l'image optimisée
            output = io.BytesIO()
            save_kwargs = {'format': image_format}
            if image_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            image.save(output, **save_kwargs)
            output.seek(0)
            
            # Remplacer l'image originale par l'image optimisée
            default_storage.save(image_path, ContentFile(output.read()))
            
            logger.info(f"Image {image_path} traitée avec succès")
            return {
                'success': True,
                'image_path': image_path,
                'width': image.width,
                'height': image.height,
                'format': image_format
            }
    
    except Exception as exc:
        logger.error(f"Erreur traitement image {image_path}: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def send_welcome_email(user_id):
    """
    Envoie un email de bienvenue à un nouvel utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
    """
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        subject = "Bienvenue sur EGOEJO"
        html_content = f"""
        <h1>Bienvenue {user.username or user.email} !</h1>
        <p>Merci de rejoindre EGOEJO, le collectif pour le vivant.</p>
        <p>Découvrez nos projets et contribuez à l'impact social.</p>
        """
        
        return send_email_task.delay(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    
    except Exception as exc:
        logger.error(f"Erreur envoi email bienvenue pour user {user_id}: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def send_notification_email(to_email, subject, message):
    """
    Envoie une notification email générique.
    
    Args:
        to_email: Adresse email destinataire
        subject: Sujet
        message: Message (sera converti en HTML)
    """
    html_content = f"<p>{message}</p>"
    return send_email_task.delay(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        text_content=message
    )

