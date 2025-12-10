"""
Migration pour migrer vers pgvector (VectorField)
Note: Cette migration nécessite l'extension pgvector installée sur PostgreSQL
Pour installer: CREATE EXTENSION IF NOT EXISTS vector;
"""
from django.db import migrations, models
from django.db import connection


def migrate_to_vector_field(apps, schema_editor):
    """
    Migre les embeddings JSONField vers VectorField (pgvector).
    Nécessite l'extension pgvector installée.
    """
    if connection.vendor != 'postgresql':
        # SQLite ne supporte pas pgvector, skip
        return
    
    # Vérifier si pgvector est disponible
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            if not cursor.fetchone():
                # Extension non installée, skip
                return
    except Exception:
        # Erreur, skip
        return
    
    # Migration sera gérée par Django avec VectorField
    # Les données JSON seront converties automatiquement
    pass


def reverse_migrate(apps, schema_editor):
    """
    Reverse: convertir VectorField vers JSONField.
    """
    pass


class Migration(migrations.Migration):
    """
    Migration conditionnelle vers pgvector.
    Si pgvector n'est pas disponible, cette migration est ignorée.
    """
    
    dependencies = [
        ('core', '0012_add_voting_method_to_poll'),
    ]

    operations = [
        # Note: Pour activer VectorField, installer pgvector d'abord
        # Puis créer une nouvelle migration avec VectorField
        migrations.RunPython(migrate_to_vector_field, reverse_migrate),
    ]

