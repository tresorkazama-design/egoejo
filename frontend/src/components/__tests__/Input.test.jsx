import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { Input } from '../Input';

describe('Input', () => {
  it('devrait afficher un input avec un label', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('devrait afficher un astérisque si required', () => {
    render(<Input label="Email" required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('devrait afficher un placeholder', () => {
    render(<Input placeholder="Entrez votre email" />);
    expect(screen.getByPlaceholderText('Entrez votre email')).toBeInTheDocument();
  });

  it('devrait afficher une erreur si fournie', () => {
    render(<Input error="Email invalide" />);
    expect(screen.getByText('Email invalide')).toBeInTheDocument();
  });

  it('devrait appeler onChange quand on tape', async () => {
    const handleChange = vi.fn();
    const user = userEvent.setup();
    
    render(<Input onChange={handleChange} />);
    const input = screen.getByRole('textbox');
    
    await user.type(input, 'test');
    expect(handleChange).toHaveBeenCalled();
  });

  it('devrait être désactivé quand disabled est true', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('devrait accepter différents types', () => {
    const { rerender } = render(<Input type="email" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email');

    rerender(<Input type="password" />);
    expect(screen.getByDisplayValue('')).toHaveAttribute('type', 'password');
  });

  it('devrait afficher la valeur', () => {
    render(<Input value="test@example.com" />);
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
  });

  it('devrait avoir la classe d\'erreur si error est présent', () => {
    render(<Input error="Erreur" />);
    const input = screen.getByRole('textbox');
    expect(input.className).toContain('border-red-500');
  });

  it('devrait accepter des props supplémentaires', () => {
    render(<Input data-testid="custom-input" aria-label="Input personnalisé" />);
    const input = screen.getByTestId('custom-input');
    expect(input).toHaveAttribute('aria-label', 'Input personnalisé');
  });
});

