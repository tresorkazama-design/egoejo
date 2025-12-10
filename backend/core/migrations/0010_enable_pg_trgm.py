"""
Migration pour activer l'extension PostgreSQL pg_trgm
Nécessaire pour la recherche full-text avec similarité trigram
Note: Cette migration ne s'exécute que sur PostgreSQL, pas sur SQLite
"""
from django.db import migrations, connection


def enable_pg_trgm(apps, schema_editor):
    """
    Active l'extension pg_trgm uniquement sur PostgreSQL
    """
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def disable_pg_trgm(apps, schema_editor):
    """
    Désactive l'extension pg_trgm (reverse migration)
    """
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("DROP EXTENSION IF EXISTS pg_trgm;")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_educationalcontent_category_educationalcontent_tags_and_more'),
    ]

    operations = [
        migrations.RunPython(
            enable_pg_trgm,
            reverse_code=disable_pg_trgm,
        ),
    ]

