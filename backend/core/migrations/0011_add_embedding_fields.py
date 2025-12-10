"""
Migration pour préparer les champs embedding (recherche vectorielle future)
Note: Cette migration prépare le schéma pour pgvector, mais ne crée pas l'extension
L'extension pgvector sera activée séparément lors de l'implémentation complète
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_enable_pg_trgm'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationalcontent',
            name='embedding',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text="Vecteur d'embedding pour recherche sémantique (pgvector future)"
            ),
        ),
        migrations.AddField(
            model_name='projet',
            name='embedding',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text="Vecteur d'embedding pour recherche sémantique (pgvector future)"
            ),
        ),
    ]

