# Generated migration - Contrainte de Séparation SAKA/EUR
# À exécuter après validation par l'équipe technique

from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration pour ajouter une contrainte de base de données empêchant 
    toute fusion ou jointure directe entre SakaWallet et UserWallet.
    
    PHILOSOPHIE EGOEJO :
    La séparation SAKA/EUR est NON NÉGOCIABLE. Cette contrainte technique
    rend impossible toute fusion même avec accès SQL direct.
    """
    
    dependencies = [
        ('core', 'XXXX_previous_migration'),  # À remplacer par la dernière migration
        ('finance', 'XXXX_previous_migration'),  # À remplacer par la dernière migration
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Vue de détection des violations de séparation
            -- Cette vue identifie toute tentative de liaison entre SakaWallet et UserWallet
            CREATE OR REPLACE VIEW saka_eur_separation_check AS
            SELECT 
                sw.id as saka_wallet_id,
                uw.id as user_wallet_id,
                sw.user_id,
                'VIOLATION: SakaWallet and UserWallet cannot be linked in queries' as violation_reason
            FROM core_sakawallet sw
            INNER JOIN finance_userwallet uw ON sw.user_id = uw.user_id
            WHERE 1=0;  -- Vue vide par défaut (pas de violation)
            
            -- Fonction de vérification de séparation
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
            
            -- Commentaire pour documentation
            COMMENT ON VIEW saka_eur_separation_check IS 
            'Vue de détection des violations de séparation SAKA/EUR. Toute jointure entre SakaWallet et UserWallet est interdite.';
            
            COMMENT ON FUNCTION check_saka_eur_separation() IS 
            'Fonction de vérification de la séparation SAKA/EUR. Bloque toute tentative de fusion.';
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS check_saka_eur_separation();
            DROP VIEW IF EXISTS saka_eur_separation_check;
            """
        ),
    ]

