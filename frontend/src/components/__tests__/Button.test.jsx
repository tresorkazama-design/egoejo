import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { Button } from '../Button';

describe('Button', () => {
  it('devrait afficher le contenu du bouton', () => {
    render(<Button>Cliquer ici</Button>);
    expect(screen.getByText('Cliquer ici')).toBeInTheDocument();
  });

  it('devrait appeler onClick quand on clique', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Cliquer</Button>);
    
    await user.click(screen.getByText('Cliquer'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('ne devrait pas appeler onClick si disabled', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} disabled>Cliquer</Button>);
    
    await user.click(screen.getByText('Cliquer'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('devrait être désactivé quand disabled est true', () => {
    render(<Button disabled>Bouton</Button>);
    expect(screen.getByText('Bouton')).toBeDisabled();
  });

  it('devrait utiliser la variante primary par défaut', () => {
    render(<Button>Bouton</Button>);
    const button = screen.getByText('Bouton');
    expect(button.className).toContain('bg-blue-600');
  });

  it('devrait appliquer la variante secondary', () => {
    render(<Button variant="secondary">Bouton</Button>);
    const button = screen.getByText('Bouton');
    expect(button.className).toContain('bg-gray-200');
  });

  it('devrait appliquer la variante danger', () => {
    render(<Button variant="danger">Supprimer</Button>);
    const button = screen.getByText('Supprimer');
    expect(button.className).toContain('bg-red-600');
  });

  it('devrait accepter un type personnalisé', () => {
    render(<Button type="submit">Soumettre</Button>);
    expect(screen.getByText('Soumettre')).toHaveAttribute('type', 'submit');
  });

  it('devrait accepter des classes personnalisées', () => {
    render(<Button className="custom-class">Bouton</Button>);
    const button = screen.getByText('Bouton');
    expect(button.className).toContain('custom-class');
  });

  it('devrait accepter des props supplémentaires', () => {
    render(<Button data-testid="custom-button" aria-label="Bouton personnalisé">Bouton</Button>);
    const button = screen.getByTestId('custom-button');
    expect(button).toHaveAttribute('aria-label', 'Bouton personnalisé');
  });
});

