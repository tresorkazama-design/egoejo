const { test, expect } = require('@playwright/test');

test.describe('Page Votes', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/polls/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify([
          {
            id: 1,
            title: 'Choix du lieu',
            question: 'Où allons-nous ?',
            status: 'open',
            total_votes: 3,
          },
        ]),
        headers: { 'Content-Type': 'application/json' },
      });
    });

    await page.route('**/api/polls/1/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          id: 1,
          title: 'Choix du lieu',
          question: 'Où allons-nous ?',
          status: 'open',
          total_votes: 3,
          allow_multiple: false,
          is_anonymous: true,
          options: [
            { id: 10, label: 'Montagne', votes: 2 },
            { id: 11, label: 'Mer', votes: 1 },
          ],
        }),
        headers: { 'Content-Type': 'application/json' },
      });
    });

    await page.route('**/api/polls/1/vote/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          id: 1,
          title: 'Choix du lieu',
          question: 'Où allons-nous ?',
          status: 'open',
          total_votes: 4,
          allow_multiple: false,
          is_anonymous: true,
          options: [
            { id: 10, label: 'Montagne', votes: 3 },
            { id: 11, label: 'Mer', votes: 1 },
          ],
        }),
        headers: { 'Content-Type': 'application/json' },
      });
    });
  });

  test('permet de voter', async ({ page }) => {
    await page.goto('/votes');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('text=Voir le détail');

    await page.getByRole('button', { name: 'Voir le détail' }).click();
    await expect(page.getByText('Montagne')).toBeVisible();
    await page.getByRole('radio', { name: 'Montagne' }).check();
    await page.getByRole('button', { name: 'Voter' }).click();
    await expect(page.getByText('Vote enregistré.', { exact: false })).toBeVisible();
  });
});
