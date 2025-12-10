"""
Migration pour ajouter audio_file (TTS) et coordinates_3d (Mycélium)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_projet_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationalcontent',
            name='audio_file',
            field=models.FileField(
                blank=True,
                help_text="Fichier audio généré automatiquement (TTS) pour accessibilité terrain.",
                null=True,
                upload_to='educational_contents/audio/'
            ),
        ),
        # Note: coordinates_3d est stocké dans le champ embedding (JSONField)
        # Pas besoin de migration séparée, c'est dans le JSON
    ]

