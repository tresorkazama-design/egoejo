import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import SakaSeasonBadge from '../saka/SakaSeasonBadge';

describe('SakaSeasonBadge', () => {
  it('devrait afficher "Saison des semailles" pour un solde < 100', () => {
    render(<SakaSeasonBadge balance={0} />);
    
    expect(screen.getByText('🌱')).toBeInTheDocument();
    expect(screen.getByText('Saison des semailles')).toBeInTheDocument();
    
    const badge = screen.getByText('Saison des semailles').closest('.saka-season-badge');
    expect(badge).toHaveAttribute('data-season', 'semailles');
  });

  it('devrait afficher "Saison de croissance" pour un solde entre 100 et 499', () => {
    render(<SakaSeasonBadge balance={150} />);
    
    expect(screen.getByText('🌿')).toBeInTheDocument();
    expect(screen.getByText('Saison de croissance')).toBeInTheDocument();
    
    const badge = screen.getByText('Saison de croissance').closest('.saka-season-badge');
    expect(badge).toHaveAttribute('data-season', 'croissance');
  });

  it('devrait afficher "Saison d\'abondance" pour un solde >= 500', () => {
    render(<SakaSeasonBadge balance={800} />);
    
    expect(screen.getByText('🌾')).toBeInTheDocument();
    expect(screen.getByText("Saison d'abondance")).toBeInTheDocument();
    
    const badge = screen.getByText("Saison d'abondance").closest('.saka-season-badge');
    expect(badge).toHaveAttribute('data-season', 'abondance');
  });

  it('devrait utiliser 0 comme valeur par défaut si balance n\'est pas fournie', () => {
    render(<SakaSeasonBadge />);
    
    expect(screen.getByText('🌱')).toBeInTheDocument();
    expect(screen.getByText('Saison des semailles')).toBeInTheDocument();
  });

  it('devrait afficher "Saison de croissance" pour exactement 100', () => {
    render(<SakaSeasonBadge balance={100} />);
    
    expect(screen.getByText('🌿')).toBeInTheDocument();
    expect(screen.getByText('Saison de croissance')).toBeInTheDocument();
  });

  it('devrait afficher "Saison d\'abondance" pour exactement 500', () => {
    render(<SakaSeasonBadge balance={500} />);
    
    expect(screen.getByText('🌾')).toBeInTheDocument();
    expect(screen.getByText("Saison d'abondance")).toBeInTheDocument();
  });

  it('devrait afficher "Saison des semailles" pour 99', () => {
    render(<SakaSeasonBadge balance={99} />);
    
    expect(screen.getByText('🌱')).toBeInTheDocument();
    expect(screen.getByText('Saison des semailles')).toBeInTheDocument();
  });
});

