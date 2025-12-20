"""
Tâches asynchrones Celery pour traitement en arrière-plan
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.utils import OperationalError, DatabaseError
import os
import resend
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# PROTECTION RETRY : Constantes pour gestion des retries
MAX_RETRIES_TASKS = 3
RETRY_ONLY_TEMPORARY_ERRORS = True  # Ne retry que les erreurs temporaires


@shared_task(bind=True, max_retries=3)
def notify_project_success_task(self, project_id):
    """
    Tâche Celery pour notifier les donateurs/investisseurs du succès d'un projet.
    CORRECTION 4 : Asynchronisme pour éviter timeout lors de la clôture.
    
    OPTIMISATION N+1 : Batch processing au lieu d'une task par email.
    
    Args:
        project_id: ID du projet qui a réussi
    """
    try:
        from core.models import Projet
        from finance.models import EscrowContract
        
        # OPTIMISATION N+1 : Limite stricte pour éviter explosion de tasks
        MAX_ESCROWS_PER_NOTIFICATION = 1000
        EMAIL_BATCH_SIZE = 50
        
        project = Projet.objects.get(id=project_id)
        
        # Récupérer tous les escrows libérés pour ce projet (avec limite)
        escrows_qs = EscrowContract.objects.filter(
            project=project,
            status='RELEASED'
        ).select_related('user')
        
        total_escrows_count = escrows_qs.count()
        
        if total_escrows_count > MAX_ESCROWS_PER_NOTIFICATION:
            logger.warning(
                f"Projet {project_id} a {total_escrows_count} escrows (> {MAX_ESCROWS_PER_NOTIFICATION}), "
                f"traitement limité à {MAX_ESCROWS_PER_NOTIFICATION}"
            )
        
        escrows = list(escrows_qs[:MAX_ESCROWS_PER_NOTIFICATION])
        
        # OPTIMISATION N+1 : Préparer les emails en batch au lieu d'une task par email
        emails_to_send = []
        for escrow in escrows:
            if escrow.user and escrow.user.email:
                emails_to_send.append({
                    'to_email': escrow.user.email,
                    'subject': f"🎉 Le projet '{project.titre}' a réussi !",
                    'html_content': f"""
                    <h1>Félicitations !</h1>
                    <p>Le projet <strong>{project.titre}</strong> a atteint son objectif.</p>
                    <p>Votre contribution de <strong>{escrow.amount} €</strong> a été libérée.</p>
                    <p>Merci pour votre soutien !</p>
                    """
                })
        
        # OPTIMISATION N+1 : Envoyer par batch au lieu d'une task par email
        notified_count = 0
        for i in range(0, len(emails_to_send), EMAIL_BATCH_SIZE):
            batch = emails_to_send[i:i + EMAIL_BATCH_SIZE]
            send_batch_email_task.delay(batch)
            notified_count += len(batch)
        
        logger.info(f"Notifications batchées pour le projet {project_id} ({notified_count}/{total_escrows_count} contributeurs)")
        return {'success': True, 'notified_count': notified_count, 'total_escrows': total_escrows_count}
    
    except (OperationalError, DatabaseError) as exc:
        # PROTECTION RETRY : Erreur temporaire DB (lock timeout, connexion) - retry
        logger.warning(f"Erreur temporaire DB notification projet {project_id}: {exc}")
        if self.request.retries < MAX_RETRIES_TASKS:
            raise self.retry(exc=exc, countdown=60)
        else:
            logger.error(f"Nombre maximum de retries atteint pour notification projet {project_id}")
            raise
    except Exception as exc:
        # PROTECTION RETRY : Erreur logique/permanente - ne pas retry, logger en ERROR
        logger.error(f"Erreur permanente notification projet {project_id}: {exc}", exc_info=True)
        # Ne pas retry sur erreurs logiques (projet introuvable, données invalides, etc.)
        raise


@shared_task(bind=True, max_retries=3)
def send_batch_email_task(self, emails_batch):
    """
    Envoie un batch d'emails de manière asynchrone via Resend.
    
    OPTIMISATION N+1 : Traite plusieurs emails en une seule task au lieu d'une task par email.
    
    Args:
        emails_batch: Liste de dictionnaires avec 'to_email', 'subject', 'html_content', 'text_content' (optionnel)
    
    Returns:
        dict: Résultat de l'envoi avec succès/échecs
    """
    try:
        resend_api_key = os.environ.get('RESEND_API_KEY')
        if not resend_api_key:
            logger.warning("RESEND_API_KEY non configuré, emails non envoyés")
            return {'success': False, 'error': 'RESEND_API_KEY not configured', 'sent': 0, 'failed': len(emails_batch)}
        
        resend.api_key = resend_api_key
        from_email = os.environ.get('NOTIFY_EMAIL', 'noreply@egoejo.org')
        
        sent_count = 0
        failed_count = 0
        
        # Envoyer chaque email du batch
        for email_data in emails_batch:
            try:
                params = {
                    "from": from_email,
                    "to": [email_data['to_email']],
                    "subject": email_data['subject'],
                    "html": email_data['html_content'],
                }
                
                if email_data.get('text_content'):
                    params["text"] = email_data['text_content']
                
                email = resend.Emails.send(params)
                sent_count += 1
                logger.debug(f"Email envoyé avec succès à {email_data['to_email']}: {email.get('id')}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Erreur envoi email à {email_data['to_email']}: {e}", exc_info=True)
        
        logger.info(f"Batch email terminé: {sent_count} envoyés, {failed_count} échoués sur {len(emails_batch)}")
        return {'success': True, 'sent': sent_count, 'failed': failed_count, 'total': len(emails_batch)}
    
    except (ConnectionError, TimeoutError) as exc:
        # PROTECTION RETRY : Erreur temporaire réseau - retry
        logger.warning(f"Erreur temporaire réseau lors de l'envoi du batch d'emails: {exc}")
        if self.request.retries < MAX_RETRIES_TASKS:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Nombre maximum de retries atteint pour batch emails")
            raise
    except Exception as exc:
        # PROTECTION RETRY : Erreur logique/permanente (API key invalide, format invalide) - ne pas retry
        logger.error(f"Erreur permanente lors de l'envoi du batch d'emails: {exc}", exc_info=True)
        # Ne pas retry sur erreurs logiques (API key manquante, format invalide, etc.)
        raise


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
    
    except (ConnectionError, TimeoutError) as exc:
        # PROTECTION RETRY : Erreur temporaire réseau - retry
        logger.warning(f"Erreur temporaire réseau envoi email à {to_email}: {exc}")
        if self.request.retries < MAX_RETRIES_TASKS:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Nombre maximum de retries atteint pour email à {to_email}")
            raise
    except Exception as exc:
        # PROTECTION RETRY : Erreur logique/permanente (API key invalide, email invalide) - ne pas retry
        logger.error(f"Erreur permanente envoi email à {to_email}: {exc}", exc_info=True)
        # Ne pas retry sur erreurs logiques (API key manquante, email invalide, etc.)
        raise


@shared_task(bind=True, name='core.tasks.saka_run_compost_cycle')
def saka_run_compost_cycle(self, dry_run=False):
    """
    Tâche périodique appelée par Celery Beat pour exécuter un cycle de compostage SAKA.
    
    Phase 3 : Compostage & Silo Commun
    
    Args:
        dry_run: Si True, calcule seulement ce qui serait fait (aucune écriture)
        
    Returns:
        dict: Résultat du cycle de compostage
    """
    from core.services.saka import run_saka_compost_cycle
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        result = run_saka_compost_cycle(dry_run=dry_run, source="celery")
        logger.info(f"SAKA compost cycle result: {result}")
        return result
    except Exception as exc:
        logger.error(f"Erreur lors du cycle de compostage SAKA: {exc}", exc_info=True)
        raise


@shared_task
def saka_silo_redistribution_task():
    """
    Tâche Celery pour redistribuer le Silo Commun SAKA.
    
    Phase 3 : Compostage & Silo Commun - Redistribution
    
    Vérifie si la redistribution est activée, appelle le service de redistribution
    avec le taux configuré.
    
    Désactivée par défaut (SAKA_SILO_REDIS_ENABLED=False).
    
    Returns:
        dict: Résultat de la redistribution avec stats
    """
    from django.conf import settings
    from core.services.saka import redistribute_saka_silo
    
    if not getattr(settings, "SAKA_SILO_REDIS_ENABLED", False):
        return {"ok": False, "reason": "disabled"}
    
    rate = float(getattr(settings, "SAKA_SILO_REDIS_RATE", 0.1))
    stats = redistribute_saka_silo(rate=rate)
    return {"ok": True, **stats}


@shared_task
def saka_silo_redistribution_task():
    """
    Tâche Celery pour redistribuer le Silo Commun SAKA.
    
    Phase 3 : Compostage & Silo Commun - Redistribution
    
    Vérifie si la redistribution est activée, appelle le service de redistribution
    avec le taux configuré.
    
    Désactivée par défaut (SAKA_SILO_REDIS_ENABLED=False).
    
    Returns:
        dict: Résultat de la redistribution avec stats
    """
    from django.conf import settings
    from core.services.saka import redistribute_saka_silo
    
    if not getattr(settings, "SAKA_SILO_REDIS_ENABLED", False):
        return {"ok": False, "reason": "disabled"}
    
    rate = float(getattr(settings, "SAKA_SILO_REDIS_RATE", 0.1))
    stats = redistribute_saka_silo(rate=rate)
    return {"ok": True, **stats}


@shared_task(bind=True, name='core.tasks.run_saka_silo_redistribution')
def run_saka_silo_redistribution(self):
    """
    Tâche périodique appelée par Celery Beat pour redistribuer le Silo Commun SAKA.
    
    Phase 3 : Compostage & Silo Commun - Redistribution
    
    Vérifie si la redistribution est activée, appelle le service de redistribution,
    et loggue les résultats pour le monitoring.
    
    Désactivée par défaut (SAKA_SILO_REDIS_ENABLED=False).
    Utile pour tester ou activer manuellement.
    
    Returns:
        dict: Résultat de la redistribution avec stats
    """
    from django.conf import settings
    from core.services.saka import redistribute_saka_silo
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Vérifier si la redistribution est activée
    if not getattr(settings, "SAKA_SILO_REDIS_ENABLED", False):
        logger.info("Redistribution SAKA Silo désactivée (SAKA_SILO_REDIS_ENABLED=False)")
        return {"ok": False, "reason": "disabled"}
    
    try:
        # Appeler le service de redistribution
        result = redistribute_saka_silo()
        
        # Logger les résultats pour le monitoring
        if result.get("ok"):
            logger.info(
                f"Redistribution SAKA Silo réussie : "
                f"{result.get('redistributed', 0)} grains redistribués à "
                f"{result.get('eligible_wallets', 0)} wallets "
                f"({result.get('per_wallet', 0)} grains chacun). "
                f"Silo : {result.get('total_before', 0)} → {result.get('total_after', 0)}"
            )
        else:
            logger.warning(
                f"Redistribution SAKA Silo non effectuée : {result.get('reason', 'unknown')}"
            )
        
        return result
        
    except Exception as exc:
        logger.error(
            f"Erreur lors de la redistribution du Silo SAKA : {exc}",
            exc_info=True
        )
        raise


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

