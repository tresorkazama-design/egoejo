"""
Architecture des Oracles d'Impact
Permet l'intégration de données externes (API) pour enrichir les scores P3 et P4

Architecture :
- BaseImpactOracle : Classe abstraite pour tous les oracles
- Implémentations concrètes : CO2AvoidedOracle, SocialImpactOracle, etc.
- Intégration dans le modèle Project via active_oracles

⚠️ ATTENTION : Cette architecture prépare la "tuyauterie" pour ingérer des données externes.
Elle n'est PAS encore connectée au calcul final des scores P3/P4.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from decimal import Decimal
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# PROTECTION TIMEOUT : Limite stricte sur le nombre d'oracles actifs
MAX_ORACLES_PER_PROJECT = 10

# PROTECTION TIMEOUT : Timeout par défaut pour les appels API externes (secondes)
DEFAULT_API_TIMEOUT = 10


class OracleError(Exception):
    """Exception spécifique aux erreurs d'oracle"""
    pass


class BaseImpactOracle(ABC):
    """
    Classe abstraite de base pour tous les oracles d'impact.
    
    Un oracle est une source de données externe qui fournit des métriques d'impact
    vérifiées pour un projet. Les oracles peuvent être :
    - APIs carbone (CO2 évité)
    - APIs sociales (emplois créés, personnes impactées)
    - APIs environnementales (biodiversité, eau)
    - APIs de certification (labels, certifications)
    
    Chaque oracle doit implémenter :
    - fetch_impact_data() : Récupère les données d'impact depuis la source externe
    - validate_data() : Valide les données récupérées
    - get_impact_metrics() : Extrait les métriques pertinentes pour P3/P4
    """
    
    # Identifiant unique de l'oracle (utilisé dans active_oracles du projet)
    oracle_id: str = None
    
    # Nom lisible de l'oracle
    name: str = None
    
    # Description de ce que mesure l'oracle
    description: str = None
    
    # Dimensions d'impact couvertes (P3, P4, ou les deux)
    impact_dimensions: List[str] = []  # ['P3', 'P4']
    
    # Configuration de l'oracle (API keys, endpoints, etc.)
    config: Dict[str, Any] = {}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise l'oracle avec sa configuration.
        
        Args:
            config: Dictionnaire de configuration (API keys, endpoints, etc.)
        """
        if config:
            self.config = config
        else:
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration par défaut de l'oracle.
        Peut être surchargée par les sous-classes.
        
        Returns:
            Dict de configuration par défaut
        """
        return {}
    
    @abstractmethod
    def fetch_impact_data(self, project: 'Projet') -> Dict[str, Any]:
        """
        Récupère les données d'impact depuis la source externe.
        
        Cette méthode doit :
        1. Faire l'appel API externe (ou simuler)
        2. Parser la réponse
        3. Retourner un dictionnaire structuré
        
        Args:
            project: Instance du projet Projet pour lequel récupérer les données
        
        Returns:
            Dict contenant les données brutes d'impact :
            {
                'raw_data': {...},  # Données brutes de l'API
                'timestamp': '2025-12-19T10:00:00Z',
                'source': 'oracle_id',
                'status': 'success' | 'error',
                'error': 'message' (si status='error')
            }
        
        Raises:
            OracleError: Si l'appel API échoue ou les données sont invalides
        """
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Valide les données récupérées par fetch_impact_data().
        
        Args:
            data: Données retournées par fetch_impact_data()
        
        Returns:
            True si les données sont valides, False sinon
        """
        if not isinstance(data, dict):
            return False
        
        required_keys = ['raw_data', 'timestamp', 'source', 'status']
        return all(key in data for key in required_keys)
    
    @abstractmethod
    def get_impact_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les métriques d'impact pertinentes depuis les données brutes.
        
        Cette méthode transforme les données brutes en métriques utilisables
        pour le calcul des scores P3 et P4.
        
        Args:
            data: Données validées retournées par fetch_impact_data()
        
        Returns:
            Dict contenant les métriques d'impact :
            {
                'p3_contributions': {
                    'co2_avoided_kg': 100.5,  # Exemple pour CO2
                    'social_impact_score': 75,  # Exemple pour social
                },
                'p4_contributions': {
                    'purpose_alignment': 0.85,  # Exemple pour purpose
                },
                'metadata': {
                    'last_updated': '2025-12-19T10:00:00Z',
                    'source': 'oracle_id',
                    'confidence': 0.9,  # Niveau de confiance (0-1)
                }
            }
        """
        pass
    
    def get_oracle_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'oracle (métadonnées).
        
        Returns:
            Dict contenant les informations de l'oracle
        """
        return {
            'oracle_id': self.oracle_id,
            'name': self.name,
            'description': self.description,
            'impact_dimensions': self.impact_dimensions,
            'config_keys': list(self.config.keys()),
        }
    
    def is_enabled(self) -> bool:
        """
        Vérifie si l'oracle est activé (configuration présente).
        
        Returns:
            True si l'oracle peut être utilisé, False sinon
        """
        return True  # Par défaut, toujours activé si instancié


class CO2AvoidedOracle(BaseImpactOracle):
    """
    Oracle pour mesurer le CO2 évité par un projet.
    
    Exemple d'implémentation qui pourrait appeler une API carbone réelle
    (ex: CarbonAPI, OpenCarbon, etc.)
    
    Pour l'instant, simule un appel API pour démontrer l'architecture.
    """
    
    oracle_id = 'co2_avoided'
    name = 'Oracle CO2 Évité'
    description = 'Mesure la quantité de CO2 évitée par le projet (en kg CO2e)'
    impact_dimensions = ['P3']  # Contribue au score P3 (social/écologique)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut pour l'oracle CO2"""
        impact_oracles_config = getattr(settings, 'IMPACT_ORACLES', {})
        return {
            'api_endpoint': impact_oracles_config.get('CO2_API_ENDPOINT', 'https://api.carbon.example.com/v1/calculate'),
            'api_key': impact_oracles_config.get('CO2_API_KEY', ''),
            'timeout': 10,  # secondes
            'cache_duration': 3600,  # secondes (1 heure)
        }
    
    def fetch_impact_data(self, project: 'Projet') -> Dict[str, Any]:
        """
        Récupère les données de CO2 évité depuis l'API externe.
        
        Pour l'instant, simule un appel API. Dans une implémentation réelle,
        on ferait un appel HTTP à l'API carbone.
        
        Args:
            project: Instance du projet Projet
        
        Returns:
            Dict contenant les données de CO2 évité
        """
        from datetime import datetime
        
        try:
            # PROTECTION TIMEOUT : Dans une implémentation réelle, on ferait :
            # import requests
            # from requests.exceptions import Timeout, RequestException
            # try:
            #     response = requests.get(
            #         self.config['api_endpoint'],
            #         params={'project_id': project.id, 'category': project.categorie},
            #         headers={'Authorization': f"Bearer {self.config['api_key']}"},
            #         timeout=self.config.get('timeout', DEFAULT_API_TIMEOUT)  # ✅ TIMEOUT OBLIGATOIRE
            #     )
            #     response.raise_for_status()
            #     raw_data = response.json()
            # except Timeout:
            #     logger.warning(f"Timeout lors de l'appel API CO2 pour le projet {project.id}")
            #     raise OracleError("Timeout lors de l'appel API externe")
            # except RequestException as e:
            #     logger.error(f"Erreur réseau lors de l'appel API CO2 pour le projet {project.id}: {e}")
            #     raise OracleError(f"Erreur réseau: {e}")
            
            # Pour l'instant, simulation basée sur la catégorie du projet
            co2_by_category = {
                'energie': 500.0,  # kg CO2e évités
                'transport': 300.0,
                'agriculture': 200.0,
                'foret': 1000.0,
                'eau': 150.0,
                'dechet': 250.0,
            }
            
            category = project.categorie or 'autre'
            co2_avoided = co2_by_category.get(category.lower(), 100.0)
            
            # Simulation de variabilité (pour rendre plus réaliste)
            import random
            co2_avoided *= (0.8 + random.random() * 0.4)  # ±20% de variabilité
            
            raw_data = {
                'co2_avoided_kg': round(co2_avoided, 2),
                'category': category,
                'calculation_method': 'simulated',
                'confidence': 0.7,  # Niveau de confiance (simulation = 0.7)
            }
            
            return {
                'raw_data': raw_data,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': self.oracle_id,
                'status': 'success',
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données CO2 pour le projet {project.id}: {e}", exc_info=True)
            return {
                'raw_data': {},
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': self.oracle_id,
                'status': 'error',
                'error': str(e),
            }
    
    def get_impact_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les métriques de CO2 évité pour le score P3.
        
        Args:
            data: Données validées retournées par fetch_impact_data()
        
        Returns:
            Dict contenant les métriques d'impact pour P3
        """
        if data.get('status') != 'success':
            return {
                'p3_contributions': {},
                'p4_contributions': {},
                'metadata': {
                    'last_updated': data.get('timestamp'),
                    'source': self.oracle_id,
                    'confidence': 0.0,
                    'error': data.get('error', 'Unknown error'),
                }
            }
        
        raw_data = data.get('raw_data', {})
        co2_avoided = raw_data.get('co2_avoided_kg', 0)
        confidence = raw_data.get('confidence', 0.7)
        
        return {
            'p3_contributions': {
                'co2_avoided_kg': co2_avoided,
                # On pourrait aussi calculer un score normalisé (0-100)
                'co2_score': min(100, int(co2_avoided / 10)),  # 1000 kg = 100 points
            },
            'p4_contributions': {},  # CO2 ne contribue pas à P4
            'metadata': {
                'last_updated': data.get('timestamp'),
                'source': self.oracle_id,
                'confidence': confidence,
                'calculation_method': raw_data.get('calculation_method', 'unknown'),
            }
        }


class SocialImpactOracle(BaseImpactOracle):
    """
    Oracle pour mesurer l'impact social d'un projet.
    
    Exemple : Nombre de personnes impactées, emplois créés, etc.
    """
    
    oracle_id = 'social_impact'
    name = 'Oracle Impact Social'
    description = 'Mesure l\'impact social du projet (personnes impactées, emplois créés)'
    impact_dimensions = ['P3', 'P4']  # Contribue aux scores P3 et P4
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut pour l'oracle social"""
        impact_oracles_config = getattr(settings, 'IMPACT_ORACLES', {})
        return {
            'api_endpoint': impact_oracles_config.get('SOCIAL_API_ENDPOINT', 'https://api.social.example.com/v1/impact'),
            'api_key': impact_oracles_config.get('SOCIAL_API_KEY', ''),
            'timeout': 10,
        }
    
    def fetch_impact_data(self, project: 'Projet') -> Dict[str, Any]:
        """
        Récupère les données d'impact social depuis l'API externe.
        
        Args:
            project: Instance du projet Projet
        
        Returns:
            Dict contenant les données d'impact social
        """
        from datetime import datetime
        
        try:
            # SIMULATION : Dans une implémentation réelle, appel API réel
            # Pour l'instant, simulation basée sur la description du projet
            description_length = len(project.description or '')
            
            # Simulation : plus la description est longue, plus l'impact est grand
            # (logique simplifiée pour démonstration)
            people_impacted = min(1000, description_length // 10)
            jobs_created = min(50, description_length // 100)
            
            raw_data = {
                'people_impacted': people_impacted,
                'jobs_created': jobs_created,
                'calculation_method': 'simulated',
                'confidence': 0.6,  # Simulation = confiance plus faible
            }
            
            return {
                'raw_data': raw_data,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': self.oracle_id,
                'status': 'success',
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données sociales pour le projet {project.id}: {e}", exc_info=True)
            return {
                'raw_data': {},
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': self.oracle_id,
                'status': 'error',
                'error': str(e),
            }
    
    def get_impact_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les métriques d'impact social pour P3 et P4.
        
        Args:
            data: Données validées retournées par fetch_impact_data()
        
        Returns:
            Dict contenant les métriques d'impact pour P3 et P4
        """
        if data.get('status') != 'success':
            return {
                'p3_contributions': {},
                'p4_contributions': {},
                'metadata': {
                    'last_updated': data.get('timestamp'),
                    'source': self.oracle_id,
                    'confidence': 0.0,
                    'error': data.get('error', 'Unknown error'),
                }
            }
        
        raw_data = data.get('raw_data', {})
        people_impacted = raw_data.get('people_impacted', 0)
        jobs_created = raw_data.get('jobs_created', 0)
        confidence = raw_data.get('confidence', 0.6)
        
        return {
            'p3_contributions': {
                'people_impacted': people_impacted,
                'jobs_created': jobs_created,
                'social_impact_score': min(100, int(people_impacted / 10) + jobs_created * 2),
            },
            'p4_contributions': {
                'purpose_alignment': min(1.0, (people_impacted / 1000) * 0.5 + (jobs_created / 50) * 0.5),
            },
            'metadata': {
                'last_updated': data.get('timestamp'),
                'source': self.oracle_id,
                'confidence': confidence,
                'calculation_method': raw_data.get('calculation_method', 'unknown'),
            }
        }


# Registre des oracles disponibles
ORACLE_REGISTRY: Dict[str, type] = {
    'co2_avoided': CO2AvoidedOracle,
    'social_impact': SocialImpactOracle,
}


def get_oracle(oracle_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseImpactOracle]:
    """
    Factory function pour obtenir une instance d'oracle.
    
    Args:
        oracle_id: Identifiant de l'oracle (ex: 'co2_avoided')
        config: Configuration optionnelle pour l'oracle
    
    Returns:
        Instance de l'oracle, ou None si l'oracle n'existe pas
    """
    oracle_class = ORACLE_REGISTRY.get(oracle_id)
    if not oracle_class:
        logger.warning(f"Oracle '{oracle_id}' non trouvé dans le registre")
        return None
    
    try:
        return oracle_class(config=config)
    except Exception as e:
        logger.error(f"Erreur lors de l'instanciation de l'oracle '{oracle_id}': {e}", exc_info=True)
        return None


def fetch_all_oracles_data(project: 'Projet', active_oracles: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Récupère les données de tous les oracles actifs pour un projet.
    
    PROTECTION TIMEOUT : Limite stricte sur le nombre d'oracles pour éviter les timeouts.
    
    Args:
        project: Instance du projet Projet
        active_oracles: Liste des identifiants d'oracles actifs (ex: ['co2_avoided', 'social_impact'])
    
    Returns:
        Dict contenant les données de chaque oracle :
        {
            'co2_avoided': {
                'data': {...},
                'metrics': {...},
                'status': 'success' | 'error'
            },
            ...
        }
    """
    results = {}
    
    # PROTECTION TIMEOUT : Limiter le nombre d'oracles pour éviter les timeouts
    if len(active_oracles) > MAX_ORACLES_PER_PROJECT:
        logger.warning(
            f"Projet {project.id} a {len(active_oracles)} oracles actifs (> {MAX_ORACLES_PER_PROJECT}), "
            f"traitement limité à {MAX_ORACLES_PER_PROJECT}"
        )
        active_oracles = active_oracles[:MAX_ORACLES_PER_PROJECT]
    
    for oracle_id in active_oracles:
        oracle = get_oracle(oracle_id)
        if not oracle:
            results[oracle_id] = {
                'status': 'error',
                'error': f"Oracle '{oracle_id}' non trouvé",
            }
            continue
        
        try:
            # PROTECTION TIMEOUT : Récupérer les données brutes (avec timeout géré par l'oracle)
            data = oracle.fetch_impact_data(project)
            
            # Valider les données
            if not oracle.validate_data(data):
                results[oracle_id] = {
                    'status': 'error',
                    'error': 'Données invalides',
                }
                continue
            
            # Extraire les métriques
            metrics = oracle.get_impact_metrics(data)
            
            results[oracle_id] = {
                'data': data,
                'metrics': metrics,
                'status': data.get('status', 'error'),
            }
            
        except OracleError as e:
            # PROTECTION TIMEOUT : Erreur spécifique Oracle (timeout, erreur API) - ne pas crasher
            logger.warning(f"Erreur Oracle '{oracle_id}' pour le projet {project.id}: {e}")
            results[oracle_id] = {
                'status': 'error',
                'error': str(e),
            }
        except Exception as e:
            # PROTECTION TIMEOUT : Erreur inattendue - logger mais ne pas crasher
            logger.error(f"Erreur inattendue lors de la récupération des données de l'oracle '{oracle_id}' pour le projet {project.id}: {e}", exc_info=True)
            results[oracle_id] = {
                'status': 'error',
                'error': str(e),
            }
    
    return results

