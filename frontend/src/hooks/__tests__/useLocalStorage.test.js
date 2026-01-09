import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useState } from 'react';

// Hook personnalisé useLocalStorage
export const useLocalStorage = (key, initialValue) => {
  // État pour stocker la valeur
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  // Fonction pour mettre à jour la valeur
  const setValue = (value) => {
    try {
      // Permettre à value d'être une fonction pour avoir la même API que useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
};

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.getItem.mockClear();
    localStorage.setItem.mockClear();
  });

  it('devrait retourner la valeur initiale si aucune valeur n\'est stockée', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    expect(result.current[0]).toBe('initial');
    expect(localStorage.getItem).toHaveBeenCalledWith('test-key');
  });

  it('devrait retourner la valeur stockée dans localStorage', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));

    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    expect(result.current[0]).toBe('stored-value');
  });

  it('devrait mettre à jour la valeur dans localStorage', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    act(() => {
      result.current[1]('new-value');
    });

    expect(result.current[0]).toBe('new-value');
    expect(localStorage.setItem).toHaveBeenCalledWith('test-key', JSON.stringify('new-value'));
  });

  it('devrait accepter une fonction comme valeur de mise à jour', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 0));

    act(() => {
      result.current[1]((prev) => prev + 1);
    });

    expect(result.current[0]).toBe(1);
    expect(localStorage.setItem).toHaveBeenCalledWith('test-key', JSON.stringify(1));
  });

  it('devrait gérer les objets complexes', () => {
    const initialObject = { name: 'Test', count: 0 };
    const { result } = renderHook(() => useLocalStorage('test-key', initialObject));

    act(() => {
      result.current[1]({ name: 'Updated', count: 5 });
    });

    expect(result.current[0]).toEqual({ name: 'Updated', count: 5 });
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'test-key',
      JSON.stringify({ name: 'Updated', count: 5 })
    );
  });

  it('devrait gérer les erreurs de parsing JSON', () => {
    // Simuler un localStorage corrompu
    localStorage.getItem.mockReturnValueOnce('invalid-json{');

    const { result } = renderHook(() => useLocalStorage('test-key', 'fallback'));

    // Devrait retourner la valeur initiale en cas d'erreur
    expect(result.current[0]).toBe('fallback');
  });
});

