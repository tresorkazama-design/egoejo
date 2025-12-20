"""
Service pour calculer et mettre à jour les scores 4P (Performance Partagée) par projet.

Les 4 dimensions :
- P1 : Performance financière (euros mobilisés)
  → Dérivé d'agrégats financiers réels (contributions, escrows)

- P2 : Performance vivante (SAKA mobilisé)
  → Dérivé de SAKA réellement mobilisé (supporters, boosts)

- P3 : Performance sociale/écologique (score d'impact agrégé)
  → PROXY V1 INTERNE : Utilise impact_score du projet (ou 0)
  → À ne pas interpréter comme mesure académique d'impact
  → Sera affiné avec des données d'impact plus riches dans les versions futures

- P4 : Purpose / Sens (indicateur qualitatif)
  → PROXY V1 INTERNE : Formule simplifiée basée sur supporters SAKA + cagnottes
  → À ne pas interpréter comme mesure académique d'impact
  → Sera affiné avec des indicateurs qualitatifs plus robustes dans les versions futures
"""
from django.db import transaction
from django.db.models import Sum, Count
from decimal import Decimal
from typing import Optional
import logging

from core.models.impact import ProjectImpact4P
from core.models.projects import Projet
from core.models.fundraising import Cagnotte, Contribution
from finance.models import EscrowContract, WalletTransaction

logger = logging.getLogger(__name__)


class CalculationError(Exception):
    """Exception levée lorsque le calcul 4P échoue de manière critique"""
    pass


def update_project_4p(project: Projet) -> Optional[ProjectImpact4P]:
    """
    Calcule et met à jour les scores 4P pour un projet.
    
    Règles de calcul :
    - P1 (financial_score) : Somme des contributions + escrows pour ce projet (en euros)
      → Dérivé d'agrégats financiers réels
    
    - P2 (saka_score) : Score SAKA du projet (déjà calculé)
      → Dérivé de SAKA réellement mobilisé
    
    - P3 (social_score) : impact_score du projet (ou 0 si non défini)
      → PROXY V1 INTERNE : Formule simplifiée, non académique
      → À ne pas interpréter comme mesure d'impact robuste
    
    - P4 (purpose_score) : Score basé sur la cohérence (nombre de supporters SAKA, etc.)
      → PROXY V1 INTERNE : Formule simplifiée (supporters_count * 10) + (cagnottes * 5)
      → À ne pas interpréter comme mesure d'impact robuste
    
    Args:
        project: Instance du projet Projet
        
    Returns:
        ProjectImpact4P: Instance créée ou mise à jour, None si erreur
    """
    try:
        with transaction.atomic():
            # P1 : Performance financière (euros mobilisés)
            financial_score = Decimal('0')
            
            # ÉRADICATION N+1 : Via Cagnottes (contributions) - Utiliser aggregate(Sum(...)) au lieu de boucles
            # Une seule requête SQL avec SUM au lieu de N requêtes
            cagnottes = Cagnotte.objects.filter(projet=project).select_related('projet')
            cagnotte_ids = list(cagnottes.values_list('id', flat=True))
            
            if cagnotte_ids:
                # ÉRADICATION N+1 : Une seule requête avec SUM pour toutes les contributions
                contributions_total = Contribution.objects.filter(
                    cagnotte_id__in=cagnotte_ids
                ).aggregate(
                    total=Sum('montant')
                )['total'] or 0
                financial_score += Decimal(str(contributions_total))
            
            # ÉRADICATION N+1 : Via EscrowContract - Utiliser aggregate(Sum(...)) au lieu de boucles
            try:
                # Une seule requête SQL avec SUM au lieu de N requêtes
                escrows_total = EscrowContract.objects.filter(
                    project=project,
                    status__in=['LOCKED', 'RELEASED']
                ).select_related('project').aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                financial_score += Decimal(str(escrows_total))
            except Exception as e:
                # NETTOYAGE EXCEPTIONS : Logger l'erreur au lieu de passer silencieusement
                # Si EscrowContract n'existe pas ou erreur, logger mais continuer avec score partiel
                logger.error(
                    f"Erreur lors du calcul des escrows pour le projet {project.id} (P1): {e}",
                    exc_info=True
                )
                # Ne pas lever d'exception car le score P1 peut être partiel (contributions uniquement)
            
            # P2 : Performance vivante (SAKA mobilisé)
            # Utilise directement le saka_score du projet
            saka_score = project.saka_score or 0
            
            # P3 : Performance sociale/écologique
            # PROXY V1 INTERNE : Utilise l'impact_score du projet (ou 0 si non défini)
            # ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
            # Il ne doit pas être interprété comme une mesure d'impact robuste.
            # Sera affiné avec des données d'impact plus riches dans les versions futures.
            social_score = project.impact_score or 0
            
            # Enrichissement avec Oracles d'Impact (si actifs)
            # Les oracles fournissent des données externes vérifiées pour enrichir P3
            try:
                from core.services.oracle_manager import OracleManager
                oracle_data = OracleManager.get_oracle_data(project, force_refresh=False)
                
                if oracle_data and oracle_data.get('aggregated_metrics'):
                    p3_contribs = oracle_data['aggregated_metrics'].get('p3_contributions', {})
                    
                    # Agrégation des contributions P3 des oracles
                    # Exemple : CO2 évité, personnes impactées, etc.
                    oracle_p3_bonus = 0
                    
                    # CO2 évité (si disponible)
                    if 'co2_avoided_kg' in p3_contribs:
                        co2_values = [c['value'] for c in p3_contribs['co2_avoided_kg']]
                        if co2_values:
                            # 100 kg CO2 = +1 point (normalisation)
                            oracle_p3_bonus += sum(co2_values) / 100
                    
                    # Social impact score (si disponible)
                    if 'social_impact_score' in p3_contribs:
                        social_values = [c['value'] for c in p3_contribs['social_impact_score']]
                        if social_values:
                            # Utiliser la moyenne des scores sociaux
                            oracle_p3_bonus += sum(social_values) / len(social_values)
                    
                    # Ajouter le bonus oracle au score de base (sans dépasser 100)
                    social_score = min(100, int(social_score + oracle_p3_bonus))
            except Exception as e:
                # NETTOYAGE EXCEPTIONS : Logger en ERROR au lieu de DEBUG
                # Si les oracles échouent, utiliser le score de base (fallback sûr)
                logger.error(
                    f"Erreur lors de l'enrichissement P3 avec les oracles pour le projet {project.id}: {e}",
                    exc_info=True
                )
                # Ne pas lever d'exception car le score P3 peut être partiel (impact_score du projet uniquement)
            
            # P4 : Purpose / Sens
            # PROXY V1 INTERNE : Score basé sur la cohérence (nombre de supporters SAKA + nombre de cagnottes)
            # Formule simplifiée : (supporters_count * 10) + (nombre_cagnottes * 5)
            # ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
            # Il ne doit pas être interprété comme une mesure d'impact robuste.
            # Sera affiné avec des indicateurs qualitatifs plus robustes dans les versions futures.
            # ÉRADICATION N+1 : Utiliser len() sur la liste déjà chargée au lieu de .count()
            # cagnottes est déjà un QuerySet filtré, on peut utiliser len() sans requête supplémentaire
            # OU utiliser aggregate(Count(...)) si on veut vraiment éviter de charger les objets
            cagnottes_count = cagnottes.count() if cagnottes.exists() else 0
            purpose_score = (project.saka_supporters_count * 10) + (cagnottes_count * 5)
            
            # Enrichissement avec Oracles d'Impact (si actifs)
            # Les oracles fournissent des données externes vérifiées pour enrichir P4
            try:
                from core.services.oracle_manager import OracleManager
                oracle_data = OracleManager.get_oracle_data(project, force_refresh=False)
                
                if oracle_data and oracle_data.get('aggregated_metrics'):
                    p4_contribs = oracle_data['aggregated_metrics'].get('p4_contributions', {})
                    
                    # Agrégation des contributions P4 des oracles
                    # Exemple : Purpose alignment, cohérence, etc.
                    oracle_p4_bonus = 0
                    
                    # Purpose alignment (si disponible)
                    if 'purpose_alignment' in p4_contribs:
                        alignment_values = [c['value'] for c in p4_contribs['purpose_alignment']]
                        if alignment_values:
                            # Moyenne des alignements (0-1) convertie en points (0-50)
                            avg_alignment = sum(alignment_values) / len(alignment_values)
                            oracle_p4_bonus = int(avg_alignment * 50)
                    
                    # Ajouter le bonus oracle au score de base
                    purpose_score = int(purpose_score + oracle_p4_bonus)
            except Exception as e:
                # NETTOYAGE EXCEPTIONS : Logger en ERROR au lieu de DEBUG
                # Si les oracles échouent, utiliser le score de base (fallback sûr)
                logger.error(
                    f"Erreur lors de l'enrichissement P4 avec les oracles pour le projet {project.id}: {e}",
                    exc_info=True
                )
                # Ne pas lever d'exception car le score P4 peut être partiel (supporters SAKA + cagnottes uniquement)
            
            # Créer ou mettre à jour l'instance ProjectImpact4P
            impact_4p, created = ProjectImpact4P.objects.get_or_create(
                project=project,
                defaults={
                    'financial_score': financial_score,
                    'saka_score': saka_score,
                    'social_score': social_score,
                    'purpose_score': purpose_score,
                }
            )
            
            if not created:
                # Mettre à jour les scores existants
                impact_4p.financial_score = financial_score
                impact_4p.saka_score = saka_score
                impact_4p.social_score = social_score
                impact_4p.purpose_score = purpose_score
                impact_4p.save(update_fields=[
                    'financial_score',
                    'saka_score',
                    'social_score',
                    'purpose_score',
                    'updated_at'
                ])
            
            return impact_4p
            
    except CalculationError as e:
        # NETTOYAGE EXCEPTIONS : Erreur critique de calcul - logger et propager
        logger.error(
            f"Erreur critique lors du calcul 4P pour le projet {project.id}: {e}",
            exc_info=True
        )
        # Lever l'exception pour que l'appelant sache que le score est corrompu
        raise
    except Exception as e:
        # NETTOYAGE EXCEPTIONS : Erreur inattendue - logger avec contexte complet
        logger.error(
            f"Erreur inattendue lors du calcul 4P pour le projet {project.id}: {e}",
            exc_info=True
        )
        # Retourner None pour indiquer que le calcul a échoué
        return None

