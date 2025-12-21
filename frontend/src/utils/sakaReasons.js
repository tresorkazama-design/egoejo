/**
 * Utilitaire pour mapper les codes de raison SAKA vers des labels lisibles
 * Basé sur l'enum SakaReason du backend
 */

/**
 * Mappe tous les codes de raison SAKA vers des labels français
 * @param {string} reasonCode - Code de la raison (ex: 'content_read')
 * @returns {string} Label lisible en français
 */
export function getReasonLabel(reasonCode) {
  const reasonMap = {
    // Raisons de récolte (EARN)
    'content_read': 'Lecture de contenu',
    'poll_vote': 'Vote dans un sondage',
    'invite_accepted': 'Invitation acceptée',
    'invest_bonus': 'Bonus investissement',
    'manual_adjust': 'Ajustement manuel',
    
    // Raisons de dépense (SPEND)
    'project_boost': 'Boost de projet',
    'vote_intensity': 'Vote avec intensité',
    
    // Raisons système (compostage, redistribution)
    'compost': 'Compostage automatique',
    'redistribution': 'Redistribution du Silo',
    'silo_contribution': 'Contribution au Silo Commun',
    
    // Valeurs par défaut si code inconnu
  };
  
  return reasonMap[reasonCode] || reasonCode;
}

/**
 * Formate une raison avec ses métadonnées pour affichage
 * @param {string} reasonCode - Code de la raison
 * @param {Object} metadata - Métadonnées de la transaction
 * @returns {string} Label formaté avec détails
 */
export function formatReasonWithMetadata(reasonCode, metadata = {}) {
  const baseLabel = getReasonLabel(reasonCode);
  
  // Ajouter des détails depuis les métadonnées si disponibles
  if (metadata.content_title) {
    return `${baseLabel} : ${metadata.content_title}`;
  }
  if (metadata.poll_title) {
    return `${baseLabel} : ${metadata.poll_title}`;
  }
  if (metadata.project_title) {
    return `${baseLabel} : ${metadata.project_title}`;
  }
  
  return baseLabel;
}

