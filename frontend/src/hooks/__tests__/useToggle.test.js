import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useToggle } from '../useToggle';

describe('useToggle', () => {
  it('devrait initialiser avec false par défaut', () => {
    const { result } = renderHook(() => useToggle());
    expect(result.current[0]).toBe(false);
  });

  it('devrait initialiser avec la valeur fournie', () => {
    const { result } = renderHook(() => useToggle(true));
    expect(result.current[0]).toBe(true);
  });

  it('devrait toggle la valeur', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current[1].toggle();
    });

    expect(result.current[0]).toBe(true);

    act(() => {
      result.current[1].toggle();
    });

    expect(result.current[0]).toBe(false);
  });

  it('devrait mettre à true avec setTrue', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current[1].setTrue();
    });

    expect(result.current[0]).toBe(true);
  });

  it('devrait mettre à false avec setFalse', () => {
    const { result } = renderHook(() => useToggle(true));

    act(() => {
      result.current[1].setFalse();
    });

    expect(result.current[0]).toBe(false);
  });

  it('devrait permettre de définir une valeur avec setValue', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current[1].setValue(true);
    });

    expect(result.current[0]).toBe(true);

    act(() => {
      result.current[1].setValue(false);
    });

    expect(result.current[0]).toBe(false);
  });
});

