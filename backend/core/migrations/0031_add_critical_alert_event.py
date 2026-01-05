# Generated manually on 2025-01-03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_add_cms_workflow_v1_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='CriticalAlertEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text="Date et heure de création de l'événement")),
                ('severity', models.CharField(choices=[('critical', 'Critique'), ('high', 'Élevée'), ('medium', 'Moyenne'), ('low', 'Faible')], db_index=True, default='critical', help_text="Sévérité de l'alerte", max_length=10)),
                ('event_type', models.CharField(db_index=True, help_text="Type d'événement (ex: 'INTEGRITY BREACH DETECTED', 'SAKA WALLET INCONSISTENCY')", max_length=100)),
                ('channel', models.CharField(choices=[('email', 'Email uniquement'), ('webhook', 'Webhook uniquement'), ('both', 'Email + Webhook')], db_index=True, help_text="Canal d'envoi de l'alerte", max_length=10)),
                ('fingerprint', models.CharField(db_index=True, help_text="Empreinte unique pour dédoublonnage (dedupe_key ou généré)", max_length=255)),
                ('payload_excerpt', models.JSONField(blank=True, help_text="Extrait du payload (champs principaux pour recherche rapide)", null=True)),
            ],
            options={
                'verbose_name': "Événement d'alerte critique",
                'verbose_name_plural': "Événements d'alerte critique",
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='criticalalertevent',
            index=models.Index(fields=['-created_at'], name='core_criti_created_idx'),
        ),
        migrations.AddIndex(
            model_name='criticalalertevent',
            index=models.Index(fields=['event_type', 'created_at'], name='core_criti_event_t_idx'),
        ),
        migrations.AddIndex(
            model_name='criticalalertevent',
            index=models.Index(fields=['channel', 'created_at'], name='core_criti_channel_idx'),
        ),
        migrations.AddIndex(
            model_name='criticalalertevent',
            index=models.Index(fields=['severity', 'created_at'], name='core_criti_severity_idx'),
        ),
    ]

