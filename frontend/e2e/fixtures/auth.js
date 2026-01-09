/**
 * Fixture Playwright pour l'authentification E2E
 * 
 * Usage:
 * import { test } from './fixtures/auth';
 * 
 * test('mon test', async ({ loginAsUser, gotoAuthed }) => {
 *   await loginAsUser({ user: { is_staff: true } });
 *   await gotoAuthed('/admin');
 * });
 */
import { test as base } from '@playwright/test';
import { loginAsUser as loginAsUserHelper, gotoAuthed as gotoAuthedHelper } from '../utils/test-helpers';

export const test = base.extend({
  /**
   * Fixture pour authentifier un utilisateur
   * @param {Object} options - Options (user, token)
   */
  loginAsUser: async ({ page }, use) => {
    const loginFn = async (options = {}) => {
      await loginAsUserHelper(page, options);
    };
    await use(loginFn);
  },

  /**
   * Fixture pour naviguer vers une route authentifiée
   * @param {string} route - Route à visiter
   * @param {Object} options - Options (waitForSelector, timeout)
   */
  gotoAuthed: async ({ page }, use) => {
    const gotoFn = async (route, options = {}) => {
      await gotoAuthedHelper(page, route, options);
    };
    await use(gotoFn);
  },
});

export { expect } from '@playwright/test';

