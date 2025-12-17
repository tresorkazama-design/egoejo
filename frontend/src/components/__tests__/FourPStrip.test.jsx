import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import FourPStrip from '../dashboard/FourPStrip';

describe('FourPStrip', () => {
  it('devrait afficher les trois blocs avec les bonnes valeurs', () => {
    render(
      <FourPStrip
        financial={1250.50}
        saka={420}
        impact={78}
      />
    );

    // Vérifier que les trois titres sont présents
    expect(screen.getByText('Capital financier')).toBeInTheDocument();
    expect(screen.getByText('Capital vivant (SAKA)')).toBeInTheDocument();
    expect(screen.getByText('Signal social (V1 interne)')).toBeInTheDocument();

    // Vérifier les valeurs formatées
    expect(screen.getByText(/1 250,50 €/)).toBeInTheDocument();
    expect(screen.getByText(/420 SAKA/)).toBeInTheDocument();
    expect(screen.getByText(/78\/100/)).toBeInTheDocument();

    // Vérifier le microcopy SAKA
    expect(screen.getByText('Les SAKA mesurent votre engagement non monétaire.')).toBeInTheDocument();
  });

  it('devrait afficher des valeurs par défaut quand les props sont null', () => {
    render(
      <FourPStrip
        financial={null}
        saka={null}
        impact={null}
      />
    );

    // Vérifier les valeurs par défaut
    expect(screen.getByText(/0,00 €/)).toBeInTheDocument();
    expect(screen.getByText(/0 SAKA/)).toBeInTheDocument();
    expect(screen.getByText(/—/)).toBeInTheDocument();
  });

  it('devrait formater correctement les grandes valeurs SAKA', () => {
    render(
      <FourPStrip
        financial={0}
        saka={12345}
        impact={0}
      />
    );

    // Vérifier que les grandes valeurs sont formatées avec des espaces
    expect(screen.getByText(/12 345 SAKA/)).toBeInTheDocument();
  });

  it('devrait afficher les descriptions sous chaque carte', () => {
    render(
      <FourPStrip
        financial={1000}
        saka={100}
        impact={50}
      />
    );

    expect(screen.getByText('Liquidités disponibles')).toBeInTheDocument();
    expect(screen.getByText("Grains d'engagement")).toBeInTheDocument();
    expect(screen.getByText('Indicateur interne simplifié')).toBeInTheDocument();
  });
});

