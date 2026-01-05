"""
Commande management pour générer un rapport des alertes critiques.

Usage:
    python manage.py alerts_report --month 2025-01
    python manage.py alerts_report --month 2025-12
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime
from core.models.alerts import CriticalAlertEvent


class Command(BaseCommand):
    help = 'Génère un rapport des alertes critiques pour un mois donné'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            required=True,
            help='Mois au format YYYY-MM (ex: 2025-01)'
        )

    def handle(self, *args, **options):
        month_str = options['month']
        
        # Parser le format YYYY-MM
        try:
            year, month = map(int, month_str.split('-'))
            if not (1 <= month <= 12):
                raise ValueError("Le mois doit être entre 1 et 12")
        except (ValueError, AttributeError) as e:
            raise CommandError(f"Format invalide pour --month: {month_str}. Utilisez YYYY-MM (ex: 2025-01). Erreur: {e}")
        
        # Vérifier que l'année est raisonnable
        current_year = timezone.now().year
        if year < 2020 or year > current_year + 1:
            raise CommandError(f"Année invalide: {year}. Doit être entre 2020 et {current_year + 1}")
        
        # Générer le rapport
        self.stdout.write(self.style.SUCCESS(f'\n📊 RAPPORT ALERTES CRITIQUES - {month_str}\n'))
        self.stdout.write('=' * 80)
        
        # Total
        total = CriticalAlertEvent.count_critical_alerts_for_month(year, month)
        self.stdout.write(f'\n📈 Total d\'alertes: {total}')
        
        # Par event_type
        by_event_type = CriticalAlertEvent.count_by_event_type_for_month(year, month)
        if by_event_type:
            self.stdout.write(f'\n📋 Par type d\'événement:')
            for event_type, count in sorted(by_event_type.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f'  - {event_type}: {count}')
        else:
            self.stdout.write(f'\n📋 Par type d\'événement: Aucun événement')
        
        # Par channel
        by_channel = CriticalAlertEvent.count_by_channel_for_month(year, month)
        if by_channel:
            self.stdout.write(f'\n📧 Par canal:')
            for channel, count in sorted(by_channel.items(), key=lambda x: x[1], reverse=True):
                channel_display = {
                    'email': 'Email uniquement',
                    'webhook': 'Webhook uniquement',
                    'both': 'Email + Webhook'
                }.get(channel, channel)
                self.stdout.write(f'  - {channel_display}: {count}')
        else:
            self.stdout.write(f'\n📧 Par canal: Aucun événement')
        
        # Détails supplémentaires
        if total > 0:
            # Créer les dates pour la requête
            start_date = timezone.make_aware(datetime(year, month, 1, 0, 0, 0))
            if month == 12:
                end_date = timezone.make_aware(datetime(year + 1, 1, 1, 0, 0, 0))
            else:
                end_date = timezone.make_aware(datetime(year, month + 1, 1, 0, 0, 0))
            
            # Première et dernière alerte
            first_alert = CriticalAlertEvent.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).order_by('created_at').first()
            
            last_alert = CriticalAlertEvent.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).order_by('-created_at').first()
            
            if first_alert and last_alert:
                self.stdout.write(f'\n⏰ Période:')
                self.stdout.write(f'  - Première alerte: {first_alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}')
                self.stdout.write(f'  - Dernière alerte: {last_alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS(f'\n✅ Rapport généré avec succès\n'))

