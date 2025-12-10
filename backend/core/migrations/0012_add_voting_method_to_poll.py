"""
Migration pour ajouter le support de méthodes de vote avancées (Vote Quadratique, Jugement Majoritaire)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_add_embedding_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='voting_method',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('binary', 'Binaire (Oui/Non)'),
                    ('quadratic', 'Vote Quadratique'),
                    ('majority', 'Jugement Majoritaire'),
                ],
                default='binary',
                help_text="Méthode de vote utilisée pour ce sondage"
            ),
        ),
        migrations.AddField(
            model_name='poll',
            name='max_points',
            field=models.IntegerField(
                default=100,
                null=True,
                blank=True,
                help_text="Nombre maximum de points à distribuer (Vote Quadratique uniquement)"
            ),
        ),
        migrations.AddField(
            model_name='pollballot',
            name='points',
            field=models.IntegerField(
                default=1,
                null=True,
                blank=True,
                help_text="Points attribués à cette option (Vote Quadratique)"
            ),
        ),
        migrations.AddField(
            model_name='pollballot',
            name='ranking',
            field=models.IntegerField(
                null=True,
                blank=True,
                help_text="Classement de cette option (Jugement Majoritaire: 1=meilleur, N=pire)"
            ),
        ),
    ]

