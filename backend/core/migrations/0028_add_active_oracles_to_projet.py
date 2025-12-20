"""
Migration pour ajouter le champ active_oracles au modèle Projet
Permet de spécifier quels oracles d'impact sont actifs pour un projet
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_add_saka_eur_separation_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='projet',
            name='active_oracles',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Liste des identifiants d'oracles d'impact actifs pour ce projet (ex: ['co2_avoided', 'social_impact'])",
            ),
        ),
    ]

