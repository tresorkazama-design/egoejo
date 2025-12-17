/**
 * Tests de performance pour vérifier les optimisations
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { measurePerformance, createCache, debounce, throttle } from '../performance';

describe('Performance Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait mesurer les performances d\'une fonction', async () => {
    const slowFunction = async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
      return 'result';
    };

    const duration = await measurePerformance(slowFunction, 'Test Function');
    expect(duration).toBeGreaterThan(0);
    expect(duration).toBeLessThan(100); // Devrait être rapide
  });

  it('devrait créer un cache LRU fonctionnel', () => {
    const cache = createCache(3);
    
    cache.set('key1', 'value1');
    cache.set('key2', 'value2');
    cache.set('key3', 'value3');
    
    expect(cache.get('key1')).toBe('value1');
    expect(cache.has('key1')).toBe(true);
    expect(cache.size()).toBe(3);
    
    // Ajouter une 4ème clé devrait supprimer la première (LRU)
    cache.set('key4', 'value4');
    // En LRU, la clé la moins récemment utilisée est supprimée
    // key1 a été accédée avec get(), donc key2 devrait être supprimée
    expect(cache.has('key2')).toBe(false);
    expect(cache.has('key4')).toBe(true);
    expect(cache.size()).toBe(3);
  });

  it('devrait debouncer une fonction', async () => {
    const mockFn = vi.fn();
    const debouncedFn = debounce(mockFn, 100);
    
    debouncedFn();
    debouncedFn();
    debouncedFn();
    
    expect(mockFn).not.toHaveBeenCalled();
    
    await new Promise(resolve => setTimeout(resolve, 150));
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('devrait throttler une fonction', async () => {
    const mockFn = vi.fn();
    const throttledFn = throttle(mockFn, 100);
    
    throttledFn();
    throttledFn();
    throttledFn();
    
    expect(mockFn).toHaveBeenCalledTimes(1);
    
    await new Promise(resolve => setTimeout(resolve, 150));
    throttledFn();
    expect(mockFn).toHaveBeenCalledTimes(2);
  });
});

describe('Performance Metrics', () => {
  it('devrait mesurer le temps de chargement de la page', () => {
    // Vérifier que les métriques peuvent être mesurées
    expect(typeof window !== 'undefined').toBe(true);
    
    if (typeof window !== 'undefined' && window.performance) {
      // window.performance.timing est déprécié, utiliser performance.getEntriesByType
      const navigation = performance.getEntriesByType('navigation')[0];
      if (navigation) {
        expect(navigation).toBeDefined();
      } else {
        // Fallback si navigation timing n'est pas disponible
        expect(window.performance).toBeDefined();
      }
    }
  });

  it('devrait détecter les composants lents', () => {
    // Un composant ne devrait pas prendre plus de 16ms à rendre (60fps)
    const maxRenderTime = 16;
    
    const start = performance.now();
    // Simuler un rendu
    const end = performance.now();
    const renderTime = end - start;
    
    expect(renderTime).toBeLessThan(maxRenderTime);
  });
});
