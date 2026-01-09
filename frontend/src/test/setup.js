import { expect, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';
import { server } from './mocks/server';

// Étendre Vitest avec les matchers de jest-dom
expect.extend(matchers);

// Nettoyer après chaque test
afterEach(() => {
  cleanup();
});

// Mock de localStorage avec vi.spyOn pour pouvoir vérifier les appels
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = String(value);
    }),
    removeItem: vi.fn((key) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Setup MSW
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => {
  server.resetHandlers();
  cleanup();
});
afterAll(() => server.close());

// Mock de window.matchMedia (pour HeroSorgho et autres composants)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: query.includes('prefers-reduced-motion') ? false : false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver (utilisé par HeroSorgho)
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock WebGL pour HeroSorgho (optionnel, mais utile pour les tests)
const mockGetContext = vi.fn();
HTMLCanvasElement.prototype.getContext = mockGetContext;
mockGetContext.mockReturnValue({
  canvas: document.createElement('canvas'),
  getParameter: vi.fn(),
});

// Mock Three.js pour éviter les problèmes dans les tests
vi.mock('three', () => {
  const mockThree = {
    WebGLRenderer: vi.fn().mockImplementation(() => ({
      setSize: vi.fn(),
      render: vi.fn(),
      dispose: vi.fn(),
      domElement: document.createElement('canvas'),
    })),
    Scene: vi.fn().mockImplementation(() => ({
      add: vi.fn(),
      remove: vi.fn(),
    })),
    PerspectiveCamera: vi.fn().mockImplementation(() => ({
      aspect: 1,
      updateProjectionMatrix: vi.fn(),
    })),
    BufferGeometry: vi.fn().mockImplementation(() => ({
      setAttribute: vi.fn(),
      getAttribute: vi.fn(() => ({
        array: new Float32Array(0),
      })),
    })),
    BufferAttribute: vi.fn().mockImplementation(() => ({})),
    PointsMaterial: vi.fn().mockImplementation(() => ({})),
    Points: vi.fn().mockImplementation(() => ({
      geometry: {},
      material: {},
    })),
    CanvasTexture: vi.fn().mockImplementation(() => ({
      needsUpdate: false,
      flipY: false,
    })),
    Color: vi.fn().mockImplementation(() => ({})),
    AdditiveBlending: 'AdditiveBlending',
    NormalBlending: 'NormalBlending',
  };
  return mockThree;
});

// Mock GSAP pour éviter les problèmes dans les tests
vi.mock('gsap', () => {
  const mockGSAP = {
    fromTo: vi.fn(),
    to: vi.fn(),
    from: vi.fn(),
    set: vi.fn(),
    getTweensOf: vi.fn(() => []),
    killTweensOf: vi.fn(),
    registerPlugin: vi.fn(),
    utils: {
      toArray: vi.fn(() => []),
    },
  };
  return { default: mockGSAP, gsap: mockGSAP };
});

// Mock GSAP ScrollTrigger
vi.mock('gsap/ScrollTrigger', () => ({
  ScrollTrigger: {
    getAll: vi.fn(() => []),
  },
}));

// Mock de fetch global (sera remplacé dans chaque test)
global.fetch = vi.fn();

// Configuration pour jest-axe
if (typeof window !== 'undefined') {
  // S'assurer que jest-axe fonctionne correctement
  window.axe = window.axe || {};
}

