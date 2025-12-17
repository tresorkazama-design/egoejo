import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { CustomCursor } from '../CustomCursor';

describe('CustomCursor', () => {
  beforeEach(() => {
    // Mock window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('ne devrait pas s\'afficher si enabled est false', () => {
    const { container } = render(<CustomCursor enabled={false} />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor).not.toBeInTheDocument();
  });

  it('ne devrait pas s\'afficher sur mobile', () => {
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: query === '(max-width: 768px)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { container } = render(<CustomCursor enabled={true} />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor).not.toBeInTheDocument();
  });

  it('devrait avoir aria-hidden="true"', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      media: '',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { container } = render(<CustomCursor enabled={true} />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor).toBeInTheDocument();
  });

  it('devrait utiliser la taille par défaut', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      media: '',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { container } = render(<CustomCursor enabled={true} size={20} />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor).toHaveStyle({ width: '20px', height: '20px' });
  });

  it('devrait utiliser la couleur par défaut', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      media: '',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { container } = render(<CustomCursor enabled={true} color="#3B82F6" />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor).toHaveStyle({ backgroundColor: 'rgb(59, 130, 246)' });
  });

  it('devrait accepter des classes personnalisées', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      media: '',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { container } = render(<CustomCursor enabled={true} className="custom-cursor" />);
    const cursor = container.querySelector('[aria-hidden="true"]');
    expect(cursor.className).toContain('custom-cursor');
  });
});

