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
from decimal import Decimal
from typing import Optional

from core.models.impact import ProjectImpact4P
from core.models.projects import Projet
from core.models.fundraising import Cagnotte, Contribution
from finance.models import EscrowContract, WalletTransaction


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
            
            # Via Cagnottes (contributions)
            cagnottes = Cagnotte.objects.filter(projet=project)
            for cagnotte in cagnottes:
                contributions = Contribution.objects.filter(cagnotte=cagnotte)
                total_contributions = sum(Decimal(str(c.montant)) for c in contributions)
                financial_score += total_contributions
            
            # Via EscrowContract (finance.models)
            try:
                escrows = EscrowContract.objects.filter(
                    project=project,
                    status__in=['LOCKED', 'RELEASED']
                )
                for escrow in escrows:
                    financial_score += Decimal(str(escrow.amount))
            except Exception:
                # Si EscrowContract n'existe pas ou erreur, ignorer
                pass
            
            # P2 : Performance vivante (SAKA mobilisé)
            # Utilise directement le saka_score du projet
            saka_score = project.saka_score or 0
            
            # P3 : Performance sociale/écologique
            # PROXY V1 INTERNE : Utilise l'impact_score du projet (ou 0 si non défini)
            # ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
            # Il ne doit pas être interprété comme une mesure d'impact robuste.
            # Sera affiné avec des données d'impact plus riches dans les versions futures.
            social_score = project.impact_score or 0
            
            # P4 : Purpose / Sens
            # PROXY V1 INTERNE : Score basé sur la cohérence (nombre de supporters SAKA + nombre de cagnottes)
            # Formule simplifiée : (supporters_count * 10) + (nombre_cagnottes * 5)
            # ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
            # Il ne doit pas être interprété comme une mesure d'impact robuste.
            # Sera affiné avec des indicateurs qualitatifs plus robustes dans les versions futures.
            purpose_score = (project.saka_supporters_count * 10) + (cagnottes.count() * 5)
            
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
            
    except Exception as e:
        # Logger l'erreur mais ne pas faire échouer l'opération principale
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors du calcul 4P pour le projet {project.id}: {e}", exc_info=True)
        return None

