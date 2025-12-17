import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/e2e/**', // Exclure les tests E2E Playwright
      '**/__tests__/performance/automated.test.js', // Exclure temporairement (problème Rollup)
    ],
    // Configuration pour éviter les problèmes de parsing Rollup
    server: {
      deps: {
        inline: ['@vitejs/plugin-react'],
      },
    },
    // Configuration pour éviter les problèmes de parsing avec Rollup
    transformMode: {
      web: [/\.[jt]sx?$/],
    },
    // Inclure les tests de performance et d'accessibilité
    include: [
      '**/*.{test,spec}.{js,jsx}',
      '**/__tests__/**/*.{js,jsx}',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.test.{js,jsx}',
        '**/*.spec.{js,jsx}',
        '**/__tests__/**',
        '**/__mocks__/**',
        'dist/',
        'build/',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

