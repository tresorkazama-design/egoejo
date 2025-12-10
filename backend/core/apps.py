import sys
from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Cette méthode s'exécute au démarrage de l'application Django.
        Nous l'utilisons pour afficher la signature du projet.
        """
        # On évite d'afficher le logo lors des migrations ou des tâches celery,
        # on veut le voir uniquement lors du 'runserver'
        if 'runserver' in sys.argv:
            self.print_signature()

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

