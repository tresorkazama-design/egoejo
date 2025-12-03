"""
Commande Django pour créer un backup de la base de données
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
import os
import subprocess
import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Crée un backup de la base de données'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Répertoire de sortie pour les backups',
        )
        parser.add_argument(
            '--keep',
            type=int,
            default=7,
            help='Nombre de backups à conserver',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        keep_count = options['keep']
        
        # Créer le répertoire de backup s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le nom du fichier de backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        db_name = settings.DATABASES['default']['NAME']
        
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            # Backup SQLite
            backup_path = os.path.join(output_dir, f'{db_name}_{timestamp}.sqlite3')
            import shutil
            shutil.copy2(db_name, backup_path)
            self.stdout.write(self.style.SUCCESS(f'Backup SQLite créé: {backup_path}'))
        else:
            # Backup PostgreSQL
            backup_path = os.path.join(output_dir, f'{db_name}_{timestamp}.sql')
            db_config = settings.DATABASES['default']
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config.get('PASSWORD', '')
            
            cmd = [
                'pg_dump',
                '-h', db_config.get('HOST', 'localhost'),
                '-p', str(db_config.get('PORT', '5432')),
                '-U', db_config.get('USER', 'postgres'),
                '-d', db_config['NAME'],
                '-f', backup_path,
            ]
            
            try:
                subprocess.run(cmd, env=env, check=True)
                self.stdout.write(self.style.SUCCESS(f'Backup PostgreSQL créé: {backup_path}'))
            except subprocess.CalledProcessError as e:
                logger.error(f'Erreur lors du backup PostgreSQL: {e}')
                self.stdout.write(self.style.ERROR('Échec du backup'))
                return
            except FileNotFoundError:
                logger.error('pg_dump non trouvé. Installez PostgreSQL client tools.')
                self.stdout.write(self.style.ERROR('pg_dump non disponible'))
                return
        
        # Nettoyer les anciens backups
        self.cleanup_old_backups(output_dir, keep_count)
        
        self.stdout.write(self.style.SUCCESS('Backup terminé avec succès'))

    def cleanup_old_backups(self, backup_dir, keep_count):
        """
        Supprime les anciens backups, en gardant seulement les N plus récents
        """
        try:
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.endswith(('.sql', '.sqlite3')):
                    filepath = os.path.join(backup_dir, filename)
                    backups.append((os.path.getmtime(filepath), filepath))
            
            # Trier par date (plus récent en premier)
            backups.sort(reverse=True)
            
            # Supprimer les anciens backups
            for _, filepath in backups[keep_count:]:
                os.remove(filepath)
                logger.info(f'Ancien backup supprimé: {filepath}')
        except Exception as e:
            logger.error(f'Erreur lors du nettoyage des backups: {e}')

