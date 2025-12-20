import sys
import logging
from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

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
        Dead Man's Switch : Vérifie que le protocole SAKA est activé en production.
        
        PHILOSOPHIE EGOEJO :
        La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.
        Elle ne peut pas être désactivée en production.
        
        Cette vérification s'exécute UNIQUEMENT en production (DEBUG=False).
        En développement/local, les flags peuvent être désactivés pour les tests.
        
        SRE Safety : Cette vérification empêche le démarrage du serveur (Gunicorn/Daphne)
        si ENABLE_SAKA est désactivé en production, évitant ainsi des erreurs de configuration critiques.
        """
        # CORRECTION TESTS : Ignorer le Dead Man's Switch en mode test
        # Les tests utilisent override_settings pour configurer ENABLE_SAKA
        if 'test' in sys.argv or 'pytest' in sys.modules or settings.DEBUG:
            logger.debug("Mode test/développement détecté : Dead Man's Switch SAKA ignoré")
            return
        
        # Dead Man's Switch : Vérifier ENABLE_SAKA en production
        # Si ENABLE_SAKA est False en production, lever une exception bloquante
        if not getattr(settings, 'ENABLE_SAKA', False):
            error_message = (
                "\n" + "="*80 + "\n"
                "🚨 CRITICAL SAFETY STOP 🚨\n"
                "="*80 + "\n\n"
                "Attempting to run Production without SAKA Protocol.\n"
                "Enable ENABLE_SAKA env var.\n\n"
                "PHILOSOPHIE EGOEJO :\n"
                "La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.\n"
                "Elle ne peut PAS être désactivée en production.\n\n"
                "ACTION REQUISE :\n"
                "Activez le protocole SAKA en définissant la variable d'environnement :\n"
                "  ENABLE_SAKA=True\n\n"
                "Le serveur ne démarrera pas tant que cette condition n'est pas remplie.\n"
                "="*80 + "\n"
            )
            
            logger.critical(error_message)
            raise ImproperlyConfigured(
                "CRITICAL SAFETY STOP: Attempting to run Production without SAKA Protocol. Enable ENABLE_SAKA env var."
            )
        
        logger.info("✅ Dead Man's Switch SAKA : Protocole SAKA activé en production")

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

