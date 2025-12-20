"""
Gestionnaire des Oracles d'Impact
Service pour gérer l'exécution et le cache des oracles
"""

from typing import Dict, List, Optional, Any
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

from core.services.impact_oracles import (
    get_oracle,
    fetch_all_oracles_data,
    ORACLE_REGISTRY,
)
from core.models.projects import Projet

logger = logging.getLogger(__name__)


class OracleManager:
    """
    Gestionnaire centralisé pour les oracles d'impact.
    
    Responsabilités :
    - Exécution des oracles actifs pour un projet
    - Cache des résultats (éviter appels API répétés)
    - Agrégation des métriques de plusieurs oracles
    - Gestion des erreurs et fallbacks
    """
    
    # Durée de cache par défaut (1 heure)
    DEFAULT_CACHE_DURATION = 3600
    
    @classmethod
    def get_oracle_data(
        cls,
        project: Projet,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère les données de tous les oracles actifs pour un projet.
        
        Args:
            project: Instance du projet Projet
            force_refresh: Si True, ignore le cache et force la récupération
        
        Returns:
            Dict contenant les données agrégées :
            {
                'oracles': {
                    'co2_avoided': {
                        'data': {...},
                        'metrics': {...},
                        'status': 'success'
                    },
                    ...
                },
                'aggregated_metrics': {
                    'p3_contributions': {...},
                    'p4_contributions': {...},
                },
                'metadata': {
                    'last_updated': '2025-12-19T10:00:00Z',
                    'oracles_count': 2,
                    'success_count': 2,
                }
            }
        """
        # Récupérer la liste des oracles actifs
        active_oracles = project.active_oracles or []
        
        if not active_oracles:
            return {
                'oracles': {},
                'aggregated_metrics': {
                    'p3_contributions': {},
                    'p4_contributions': {},
                },
                'metadata': {
                    'last_updated': timezone.now().isoformat(),
                    'oracles_count': 0,
                    'success_count': 0,
                }
            }
        
        # Vérifier le cache
        cache_key = f'oracle_data:project:{project.id}'
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"Données oracle récupérées depuis le cache pour le projet {project.id}")
                return cached_data
        
        # Récupérer les données de tous les oracles
        oracle_results = fetch_all_oracles_data(project, active_oracles)
        
        # Agrégation des métriques
        aggregated_metrics = cls._aggregate_metrics(oracle_results)
        
        # Métadonnées
        success_count = sum(1 for r in oracle_results.values() if r.get('status') == 'success')
        
        result = {
            'oracles': oracle_results,
            'aggregated_metrics': aggregated_metrics,
            'metadata': {
                'last_updated': timezone.now().isoformat(),
                'oracles_count': len(active_oracles),
                'success_count': success_count,
            }
        }
        
        # Mettre en cache
        cache.set(cache_key, result, cls.DEFAULT_CACHE_DURATION)
        
        return result
    
    @classmethod
    def _aggregate_metrics(cls, oracle_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Agrège les métriques de plusieurs oracles.
        
        Args:
            oracle_results: Résultats de tous les oracles
        
        Returns:
            Dict contenant les métriques agrégées pour P3 et P4
        """
        aggregated = {
            'p3_contributions': {},
            'p4_contributions': {},
        }
        
        for oracle_id, result in oracle_results.items():
            if result.get('status') != 'success':
                continue
            
            metrics = result.get('metrics', {})
            
            # Agrégation P3
            p3_contribs = metrics.get('p3_contributions', {})
            for key, value in p3_contribs.items():
                if key not in aggregated['p3_contributions']:
                    aggregated['p3_contributions'][key] = []
                aggregated['p3_contributions'][key].append({
                    'value': value,
                    'source': oracle_id,
                })
            
            # Agrégation P4
            p4_contribs = metrics.get('p4_contributions', {})
            for key, value in p4_contribs.items():
                if key not in aggregated['p4_contributions']:
                    aggregated['p4_contributions'][key] = []
                aggregated['p4_contributions'][key].append({
                    'value': value,
                    'source': oracle_id,
                })
        
        return aggregated
    
    @classmethod
    def get_available_oracles(cls) -> List[Dict[str, Any]]:
        """
        Retourne la liste de tous les oracles disponibles.
        
        Returns:
            Liste de dicts contenant les informations de chaque oracle
        """
        oracles_info = []
        
        for oracle_id, oracle_class in ORACLE_REGISTRY.items():
            try:
                oracle = get_oracle(oracle_id)
                if oracle:
                    oracles_info.append(oracle.get_oracle_info())
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des infos de l'oracle '{oracle_id}': {e}", exc_info=True)
        
        return oracles_info
    
    @classmethod
    def clear_cache(cls, project: Projet):
        """
        Vide le cache des données oracle pour un projet.
        
        Args:
            project: Instance du projet Projet
        """
        cache_key = f'oracle_data:project:{project.id}'
        cache.delete(cache_key)
        logger.debug(f"Cache oracle vidé pour le projet {project.id}")

