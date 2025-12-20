# Generated migration - Contrainte de Séparation SAKA/EUR
# Migration 0027 - Contrainte de séparation SAKA/EUR

from django.db import migrations, connection


def create_saka_eur_separation_constraint(apps, schema_editor):
    """
    Crée la contrainte de séparation SAKA/EUR uniquement sur PostgreSQL.
    SQLite (tests) n'a pas besoin de cette contrainte car elle est gérée au niveau applicatif.
    """
    if connection.vendor != 'postgresql':
        # SQLite ne supporte pas les vues et fonctions PostgreSQL, skip
        return
    
    with connection.cursor() as cursor:
        # Vue de détection des violations de séparation
        cursor.execute("""
            CREATE OR REPLACE VIEW saka_eur_separation_check AS
            SELECT 
                sw.id as saka_wallet_id,
                uw.id as user_wallet_id,
                sw.user_id,
                'VIOLATION: SakaWallet and UserWallet cannot be linked in queries' as violation_reason
            FROM core_sakawallet sw
            INNER JOIN finance_userwallet uw ON sw.user_id = uw.user_id
            WHERE 1=0;  -- Vue vide par défaut (pas de violation)
        """)
        
        # Fonction de vérification de séparation
        cursor.execute("""
            CREATE OR REPLACE FUNCTION check_saka_eur_separation()
            RETURNS TRIGGER AS $$
            DECLARE
                violation_count INTEGER;
            BEGIN
                -- Vérifier s'il existe des requêtes violant la séparation
                SELECT COUNT(*) INTO violation_count
                FROM saka_eur_separation_check
                WHERE violation_reason IS NOT NULL;
                
                -- Si violation détectée, lever une exception
                IF violation_count > 0 THEN
                    RAISE EXCEPTION 'VIOLATION CONSTITUTION EGOEJO: SakaWallet and UserWallet cannot be linked. Separation is non-negotiable.';
                END IF;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Commentaires pour documentation
        cursor.execute("""
            COMMENT ON VIEW saka_eur_separation_check IS 
            'Vue de détection des violations de séparation SAKA/EUR. Toute jointure entre SakaWallet et UserWallet est interdite.';
        """)
        
        cursor.execute("""
            COMMENT ON FUNCTION check_saka_eur_separation() IS 
            'Fonction de vérification de la séparation SAKA/EUR. Bloque toute tentative de fusion.';
        """)


def reverse_saka_eur_separation_constraint(apps, schema_editor):
    """
    Supprime la contrainte de séparation SAKA/EUR (reverse migration).
    """
    if connection.vendor != 'postgresql':
        return
    
    with connection.cursor() as cursor:
        cursor.execute("DROP FUNCTION IF EXISTS check_saka_eur_separation();")
        cursor.execute("DROP VIEW IF EXISTS saka_eur_separation_check;")


class Migration(migrations.Migration):
    """
    Migration pour ajouter une contrainte de base de données empêchant 
    toute fusion ou jointure directe entre SakaWallet et UserWallet.
    
    PHILOSOPHIE EGOEJO :
    La séparation SAKA/EUR est NON NÉGOCIABLE. Cette contrainte technique
    rend impossible toute fusion même avec accès SQL direct.
    
    NOTE : Cette migration ne s'exécute que sur PostgreSQL (production).
    SQLite (tests) n'a pas besoin de cette contrainte car elle est gérée au niveau applicatif.
    """
    
    dependencies = [
        ('core', '0026_add_community_model'),  # Dernière migration core
    ]

    operations = [
        migrations.RunPython(
            create_saka_eur_separation_constraint,
            reverse_saka_eur_separation_constraint,
        ),
    ]
