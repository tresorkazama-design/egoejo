import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Nettoyer après chaque test
afterEach(() => {
  cleanup();
});

// Mock de l'API
global.fetch = global.fetch || (() => {
  throw new Error('fetch is not defined. Please install a fetch polyfill.');
});

