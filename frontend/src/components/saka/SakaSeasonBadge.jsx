/**
 * Composant SakaSeasonBadge - Badge de saison SAKA basé sur le solde
 * Exprime la philosophie "temps cyclique" du protocole SAKA
 * 
 * @param {Object} props
 * @param {number} props.balance - Solde SAKA de l'utilisateur
 */
export default function SakaSeasonBadge({ balance = 0 }) {
  // Déterminer la saison selon le solde
  let season = {
    emoji: '🌱',
    label: 'Saison des semailles',
    color: '#84cc16', // Vert clair
  };

  if (balance >= 500) {
    season = {
      emoji: '🌾',
      label: "Saison d'abondance",
      color: '#f59e0b', // Doré
    };
  } else if (balance >= 100) {
    season = {
      emoji: '🌿',
      label: 'Saison de croissance',
      color: '#22c55e', // Vert
    };
  }

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.375rem',
        padding: '0.375rem 0.75rem',
        backgroundColor: `${season.color}15`, // 15 = ~8% opacity
        color: season.color,
        borderRadius: '9999px', // rounded-full
        fontSize: '0.75rem',
        fontWeight: '500',
        border: `1px solid ${season.color}40`, // 40 = ~25% opacity
        whiteSpace: 'nowrap',
      }}
      className="saka-season-badge"
      data-season={balance < 100 ? 'semailles' : balance < 500 ? 'croissance' : 'abondance'}
    >
      <span style={{ fontSize: '0.875rem' }}>{season.emoji}</span>
      <span>{season.label}</span>
    </span>
  );
}

