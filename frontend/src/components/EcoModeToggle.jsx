/**
 * Toggle pour activer/désactiver le mode éco-responsable
 */
import { useEcoMode } from '../contexts/EcoModeContext';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../utils/i18n';

export const EcoModeToggle = () => {
  const { ecoMode, setEcoMode } = useEcoMode();
  const { language } = useLanguage();

  return (
    <label className="eco-mode-toggle" style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      padding: '10px 15px',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderRadius: '8px',
      cursor: 'pointer',
      color: '#fff',
      fontSize: '14px',
    }}>
      <input
        type="checkbox"
        checked={ecoMode}
        onChange={(e) => setEcoMode(e.target.checked)}
        style={{ cursor: 'pointer' }}
        aria-label={t('eco_mode.toggle', language) || 'Mode éco-responsable'}
      />
      <span>🌱 {t('eco_mode.label', language) || 'Mode Éco'}</span>
    </label>
  );
};

