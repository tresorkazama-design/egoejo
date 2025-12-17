/**
 * Types TypeScript pour GlobalAssets (optionnel - le projet utilise JavaScript)
 * Ces types servent de documentation et peuvent être utilisés si TypeScript est activé
 */

/**
 * Informations SAKA (Capital Vivant)
 */
export type SakaInfo = {
  balance: number;
  total_harvested: number;
  total_planted: number;
  total_composted: number;
};

/**
 * Patrimoine global de l'utilisateur
 */
export type GlobalAssets = {
  cash_balance: string;
  pockets: Array<{
    id: number;
    name: string;
    type: string;
    amount: string;
  }>;
  donations: {
    total_amount: string;
    metrics_count: number;
  };
  equity_portfolio: {
    is_active: boolean;
    positions: Array<{
      project_id: number;
      project_title: string;
      shares: number;
      valuation: string;
    }>;
    valuation: string;
  };
  social_dividend: {
    estimated_value: string;
  };
  saka?: SakaInfo; // Optionnel : présent seulement si ENABLE_SAKA=True
};

