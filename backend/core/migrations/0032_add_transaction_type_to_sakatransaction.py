# Generated manually on 2026-01-07

from django.db import migrations, models


def set_transaction_type_from_direction(apps, schema_editor):
    """
    Fonction de migration pour définir transaction_type basé sur direction.
    Pour les transactions existantes :
    - EARN -> HARVEST (par défaut, peut être REDISTRIBUTION mais on ne peut pas le déterminer)
    - SPEND -> SPEND
    """
    SakaTransaction = apps.get_model('core', 'SakaTransaction')
    for transaction in SakaTransaction.objects.all():
        if transaction.direction == 'EARN':
            transaction.transaction_type = 'HARVEST'  # Valeur par défaut pour EARN
        elif transaction.direction == 'SPEND':
            transaction.transaction_type = 'SPEND'
        transaction.save(update_fields=['transaction_type'])


def reverse_set_transaction_type(apps, schema_editor):
    """Fonction inverse (pas nécessaire mais bonne pratique)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_add_critical_alert_event'),
    ]

    operations = [
        # Étape 1 : Ajouter le champ comme nullable temporairement
        migrations.AddField(
            model_name='sakatransaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('HARVEST', 'Récolte (EARN)'),
                    ('SPEND', 'Dépense (SPEND)'),
                    ('COMPOST', 'Compostage'),
                    ('REDISTRIBUTION', 'Redistribution du Silo'),
                ],
                help_text='Type de transaction (HARVEST, SPEND, COMPOST, REDISTRIBUTION)',
                max_length=20,
                null=True,  # Temporairement nullable pour la migration
            ),
        ),
        # Étape 2 : Remplir les valeurs existantes
        migrations.RunPython(set_transaction_type_from_direction, reverse_set_transaction_type),
        # Étape 3 : Rendre le champ non-nullable
        migrations.AlterField(
            model_name='sakatransaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('HARVEST', 'Récolte (EARN)'),
                    ('SPEND', 'Dépense (SPEND)'),
                    ('COMPOST', 'Compostage'),
                    ('REDISTRIBUTION', 'Redistribution du Silo'),
                ],
                help_text='Type de transaction (HARVEST, SPEND, COMPOST, REDISTRIBUTION)',
                max_length=20,
            ),
        ),
    ]

