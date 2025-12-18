import sys
import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Cette méthode s'exécute au démarrage de l'application Django.
        Nous l'utilisons pour afficher la signature du projet et connecter les signals.
        """
        # On évite d'afficher le logo lors des migrations ou des tâches celery,
        # on veut le voir uniquement lors du 'runserver'
        if 'runserver' in sys.argv:
            self.print_signature()
        
        # Vérification des feature flags SAKA en production
        # La structure relationnelle (SAKA) est PRIORITAIRE et doit être activée en production
        self.check_saka_flags_in_production()
        
        # Connecter le signal pour créer automatiquement un SakaWallet pour chaque nouvel utilisateur
        # Import ici pour éviter les imports circulaires
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from django.conf import settings
        
        @receiver(post_save, sender=settings.AUTH_USER_MODEL)
        def create_saka_wallet(sender, instance, created, **kwargs):
            """Crée automatiquement un SakaWallet pour tout nouvel utilisateur"""
            if created:
                # Import ici pour éviter les imports circulaires
                from core.models.saka import SakaWallet
                # Utiliser get_or_create pour éviter les doublons
                SakaWallet.objects.get_or_create(
                    user=instance,
                    defaults={
                        'balance': 0,
                        'total_harvested': 0,
                        'total_planted': 0,
                        'total_composted': 0,
                    }
                )

    def check_saka_flags_in_production(self):
        """
        Vérifie que les feature flags SAKA sont activés en production.
        
        PHILOSOPHIE EGOEJO :
        La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.
        Elle ne peut pas être désactivée en production.
        
        Cette vérification s'exécute UNIQUEMENT en production (DEBUG=False).
        En développement/local, les flags peuvent être désactivés pour les tests.
        """
        # Ne vérifier qu'en production (DEBUG=False)
        if settings.DEBUG:
            logger.debug("Mode développement détecté : vérification des flags SAKA ignorée")
            return
        
        # Vérifier les flags SAKA requis
        errors = []
        
        if not getattr(settings, 'ENABLE_SAKA', False):
            errors.append("ENABLE_SAKA=False")
        
        if not getattr(settings, 'SAKA_COMPOST_ENABLED', False):
            errors.append("SAKA_COMPOST_ENABLED=False")
        
        if not getattr(settings, 'SAKA_SILO_REDIS_ENABLED', False):
            errors.append("SAKA_SILO_REDIS_ENABLED=False")
        
        # Si des flags sont désactivés, lever une exception explicite
        if errors:
            error_message = (
                "\n" + "="*80 + "\n"
                "❌ ERREUR CRITIQUE : PROTOCOLE SAKA DÉSACTIVÉ EN PRODUCTION\n"
                "="*80 + "\n\n"
                "PHILOSOPHIE EGOEJO :\n"
                "La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.\n"
                "Elle ne peut PAS être désactivée en production.\n\n"
                "FLAGS DÉSACTIVÉS :\n"
                + "\n".join(f"  - {flag}" for flag in errors) + "\n\n"
                "ACTION REQUISE :\n"
                "Activez les feature flags SAKA en définissant les variables d'environnement :\n"
                "  - ENABLE_SAKA=True\n"
                "  - SAKA_COMPOST_ENABLED=True\n"
                "  - SAKA_SILO_REDIS_ENABLED=True\n\n"
                "DOCUMENTATION :\n"
                "Consultez docs/deployment/GUIDE_ACTIVATION_FEATURE_FLAGS.md\n"
                "="*80 + "\n"
            )
            
            logger.error(error_message)
            raise RuntimeError(
                "Le protocole SAKA (structure relationnelle prioritaire) est désactivé en production. "
                "Activez ENABLE_SAKA, SAKA_COMPOST_ENABLED et SAKA_SILO_REDIS_ENABLED."
            )
        
        logger.info("✅ Vérification SAKA : Tous les feature flags sont activés en production")

    def print_signature(self):
        # Codes couleurs ANSI pour le terminal
        GREEN = '\033[92m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        # Détection du mode (V1.6 ou V2.0)
        mode = "V2.0 (Active)" if getattr(settings, 'ENABLE_INVESTMENT_FEATURES', False) else "V1.6 (Donation Only)"
        status_color = GREEN if mode.startswith("V1.6") else YELLOW

        logo = f"""{GREEN}{BOLD}
      ______ _____  ____  ______      _  ____  
     |  ____/ ____|/ __ \\|  ____|    | |/ __ \\ 
     | |__ | |  __| |  | | |__       | | |  | |
     |  __|| | |_ | |  | |  __|  _   | | |  | |
     | |___| |__| | |__| | |____| |__| | |__| |
     |______\\_____|\\____/|______|\\____/ \\____/ {RESET}
        """

        print(logo)
        print(f"      {CYAN}🌱 Dedicated to the Living / Dédié au Vivant{RESET}")
        print(f"      {CYAN}🤖 System: {BOLD}The Sleeping Giant Protocol{RESET}")
        print(f"      {CYAN}⚙️  Mode:   {status_color}{mode}{RESET}")
        print(f"      {CYAN}🛡️  Admin:  {BOLD}{settings.FOUNDER_GROUP_NAME}{RESET}")
        print("\n" + "-"*50 + "\n")

