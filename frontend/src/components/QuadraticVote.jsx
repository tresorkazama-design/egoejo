/**
 * Composant pour vote quadratique fertilisé (Phase 2 SAKA)
 * Permet de distribuer des points entre les options avec intensité et boost SAKA
 */
import { useState, useEffect, useMemo } from 'react';
import { fetchAPI } from '../utils/api';
import { useGlobalAssets } from '../hooks/useGlobalAssets';
import { useNotificationContext } from '../contexts/NotificationContext';
import { logger } from '../utils/logger';
import Confetti from './ui/Confetti';

export default function QuadraticVote({ poll, onVoteSubmitted }) {
  const [votes, setVotes] = useState({});
  const [totalPoints, setTotalPoints] = useState(0);
  const [intensity, setIntensity] = useState(1); // Intensité du vote (1-5) pour Phase 2 SAKA
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sakaVoteEnabled, setSakaVoteEnabled] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const maxPoints = poll.max_points || 100;
  
  // Récupérer les assets SAKA
  const { data: assets, refetch: refetchAssets } = useGlobalAssets();
  const { showSuccess, showError } = useNotificationContext();
  
  const sakaBalance = assets?.saka?.balance ?? 0;
  const sakaCostPer = 5; // Aligné avec le backend SAKA_VOTE_COST_PER_INTENSITY
  const sakaCost = intensity * sakaCostPer;

  // OPTIMISATION UX : Calculer le poids du vote en temps réel
  // Poids = points × √(intensité SAKA)
  const voteWeight = useMemo(() => {
    if (!sakaVoteEnabled || totalPoints === 0) {
      return totalPoints; // Vote standard sans SAKA
    }
    // Formule quadratique : poids = points × √(intensité)
    const intensityMultiplier = Math.sqrt(intensity);
    return (totalPoints * intensityMultiplier).toFixed(2);
  }, [totalPoints, intensity, sakaVoteEnabled]);

  // Multiplicateur d'intensité pour affichage
  const intensityMultiplier = useMemo(() => {
    if (!sakaVoteEnabled) return 1;
    return Math.sqrt(intensity).toFixed(2);
  }, [intensity, sakaVoteEnabled]);

  // Vérifier si SAKA_VOTE_ENABLED est activé
  useEffect(() => {
    const checkSakaFeatures = async () => {
      try {
        const config = await fetchAPI('/config/features/');
        setSakaVoteEnabled(config?.saka_vote_enabled || false);
      } catch (err) {
        logger.warn('Impossible de récupérer la config SAKA, désactivation par défaut');
        setSakaVoteEnabled(false);
      }
    };
    checkSakaFeatures();
  }, []);

  // Initialiser les votes à 0 pour chaque option
  useEffect(() => {
    const initialVotes = {};
    poll.options?.forEach(option => {
      initialVotes[option.id] = 0;
    });
    setVotes(initialVotes);
  }, [poll.options]);

  // Calculer le total des points
  useEffect(() => {
    const total = Object.values(votes).reduce((sum, points) => sum + points, 0);
    setTotalPoints(total);
  }, [votes]);

  const handlePointsChange = (optionId, points) => {
    const newPoints = Math.max(0, Math.min(points, maxPoints));
    setVotes(prev => ({
      ...prev,
      [optionId]: newPoints
    }));
  };

  const handleSubmit = async () => {
    if (totalPoints > maxPoints) {
      showError(`Total de points (${totalPoints}) dépasse le maximum (${maxPoints})`);
      return;
    }

    // Vérifier le solde SAKA si la feature est activée
    if (sakaVoteEnabled && sakaBalance < sakaCost) {
      showError(`Solde SAKA insuffisant. Vous avez ${sakaBalance} SAKA, il en faut ${sakaCost} pour cette intensité.`);
      return;
    }

    setIsSubmitting(true);

    try {
      const votesData = Object.entries(votes)
        .filter(([_, points]) => points > 0)
        .map(([optionId, points]) => ({
          option_id: parseInt(optionId),
          points: points
        }));

      // Ajouter l'intensité si SAKA est activé
      const payload = {
        votes: votesData,
        ...(sakaVoteEnabled && { intensity }),
      };

      const response = await fetchAPI(`/polls/${poll.id}/vote/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      // OPTIMISATION UX : Animation de confetti pour célébrer le vote
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 2000);

      // Afficher le message de succès avec les infos SAKA
      if (sakaVoteEnabled && response.saka_info) {
        const { weight, saka_spent } = response.saka_info;
        showSuccess(
          `Votre vote a été enregistré avec un poids de ${weight.toFixed(2)} (vous avez planté ${saka_spent} SAKA).`
        );
        // Mettre à jour le solde SAKA
        await refetchAssets();
      } else {
        showSuccess('Votre vote a été enregistré avec succès.');
      }

      if (onVoteSubmitted) {
        onVoteSubmitted();
      }
    } catch (error) {
      console.error('Erreur lors du vote:', error);
      const errorMessage = error.message || 'Erreur lors de l\'envoi du vote';
      
      // Message spécifique pour solde insuffisant
      if (errorMessage.includes('insuffisant') || errorMessage.includes('Solde')) {
        showError(`Solde SAKA insuffisant. ${errorMessage}`);
      } else {
        showError(errorMessage);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const remainingPoints = maxPoints - totalPoints;
  const canSubmit = totalPoints <= maxPoints && totalPoints > 0 && !isSubmitting;
  // Désactiver si SAKA activé et solde insuffisant
  const canSubmitWithSaka = sakaVoteEnabled ? (canSubmit && sakaBalance >= sakaCost) : canSubmit;

  return (
    <div className="quadratic-vote" data-testid="quadratic-vote-component">
      {/* OPTIMISATION UX : Animation de confetti lors du vote */}
      <Confetti active={showConfetti} particleCount={60} duration={2000} />
      
      <div className="quadratic-vote__header">
        <h3>Vote Quadratique</h3>
        <p>Distribuez vos {maxPoints} points entre les options</p>
        <div className="quadratic-vote__points-info">
          <span>Points utilisés: {totalPoints} / {maxPoints}</span>
          <span className={remainingPoints < 0 ? 'error' : ''}>
            Restants: {remainingPoints}
          </span>
        </div>
        
        {/* Phase 2 SAKA : Intensité et coût avec feedback temps réel */}
        {sakaVoteEnabled && (
          <div className="quadratic-vote__saka-info" data-testid="saka-info" style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'var(--surface)', borderRadius: 'var(--radius)' }}>
            <label htmlFor="intensity-slider" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--muted)' }}>
              Intensité du vote : <span data-testid="intensity-value" style={{ fontWeight: '600', color: 'var(--accent)' }}>{intensity}</span> (coût : <span data-testid="saka-cost" style={{ fontWeight: '600', color: '#84cc16' }}>{sakaCost}</span> SAKA)
            </label>
            <input
              id="intensity-slider"
              data-testid="intensity-slider"
              type="range"
              min="1"
              max="5"
              value={intensity}
              onChange={(e) => setIntensity(parseInt(e.target.value))}
              style={{ 
                width: '100%', 
                marginBottom: '0.5rem',
                cursor: 'pointer',
                transition: 'opacity 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--muted)', marginBottom: '0.75rem' }}>
              <span>1 (min)</span>
              <span>5 (max)</span>
            </div>
            
            {/* OPTIMISATION UX : Feedback temps réel du poids du vote */}
            {totalPoints > 0 && (
              <div style={{ 
                padding: '0.75rem', 
                backgroundColor: 'var(--bg)', 
                borderRadius: 'var(--radius)', 
                marginBottom: '0.5rem',
                border: '1px solid var(--border)',
              }}>
                <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text)', marginBottom: '0.25rem' }}>
                  <strong>Poids du vote :</strong> <span style={{ color: 'var(--accent)', fontWeight: '600' }}>{voteWeight}</span>
                </p>
                <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--muted)' }}>
                  Multiplicateur : <span style={{ fontWeight: '500' }}>×{intensityMultiplier}</span> {intensity > 1 && `(${intensity > 1 ? 'Intensité ' + intensity : 'Standard'})`}
                </p>
              </div>
            )}

            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
              Grains disponibles : <span data-testid="saka-balance" style={{ fontWeight: '600', color: '#84cc16' }}>{sakaBalance}</span> SAKA
            </p>
            {sakaBalance < sakaCost && (
              <p data-testid="insufficient-warning" style={{ fontSize: '0.75rem', color: '#ff6b6b', marginTop: '0.25rem' }}>
                ⚠️ Solde insuffisant pour cette intensité
              </p>
            )}
          </div>
        )}
      </div>

      <div className="quadratic-vote__options">
        {poll.options?.map(option => (
          <div key={option.id} className="quadratic-vote__option">
            <label>{option.label}</label>
            <div className="quadratic-vote__input-group">
              <input
                type="number"
                min="0"
                max={maxPoints}
                value={votes[option.id] || 0}
                onChange={(e) => handlePointsChange(option.id, parseInt(e.target.value) || 0)}
                className="quadratic-vote__input"
              />
              <input
                type="range"
                min="0"
                max={maxPoints}
                value={votes[option.id] || 0}
                onChange={(e) => handlePointsChange(option.id, parseInt(e.target.value))}
                className="quadratic-vote__slider"
              />
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!canSubmitWithSaka}
        className={`btn btn-primary ${!canSubmitWithSaka ? 'disabled' : ''}`}
        data-testid="submit-vote-button"
      >
        {isSubmitting ? 'Envoi en cours...' : `Soumettre le vote (${totalPoints} points${sakaVoteEnabled ? `, ${sakaCost} SAKA` : ''})`}
      </button>
    </div>
  );
}

