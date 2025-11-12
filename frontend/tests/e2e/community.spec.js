     const { test, expect } = require('@playwright/test');

     const THREAD_LIST_RESPONSE = [
       {
         id: 1,
         title: 'Fil principal',
         participants: [{ username: 'Alice' }, { username: 'Bob' }],
         last_message_at: new Date().toISOString(),
       },
     ];

     const THREAD_DETAIL_RESPONSE = {
       id: 1,
       title: 'Fil principal',
       participants: [{ username: 'Alice' }, { username: 'Bob' }],
     };

     const THREAD_MESSAGES_RESPONSE = [
       {
         id: 100,
         content: 'Bienvenue sur le fil !',
         author: { username: 'Alice' },
         created_at: new Date().toISOString(),
       },
     ];

     test.describe('Page Communauté', () => {
       test.beforeEach(async ({ page }) => {
         await page.route('**/api/chat/threads**', async (route) => {
           const url = route.request().url();
           if (url.includes('/threads/1')) {
             await route.fulfill({
               status: 200,
               body: JSON.stringify(THREAD_DETAIL_RESPONSE),
               headers: { 'Content-Type': 'application/json' },
             });
             return;
           }

           await route.fulfill({
             status: 200,
             body: JSON.stringify(THREAD_LIST_RESPONSE),
             headers: { 'Content-Type': 'application/json' },
           });
         });

         await page.route('**/api/chat/messages**', async (route) => {
           const url = new URL(route.request().url());
           if (url.searchParams.get('thread') === '1') {
             await route.fulfill({
               status: 200,
               body: JSON.stringify(THREAD_MESSAGES_RESPONSE),
               headers: { 'Content-Type': 'application/json' },
             });
             return;
           }

           await route.fulfill({
             status: 200,
             body: JSON.stringify([]),
             headers: { 'Content-Type': 'application/json' },
           });
         });
       });

       test('permet de lire un fil', async ({ page }) => {
         page.on('request', (req) => console.info('→', req.method(), req.url()));
         page.on('response', (res) =>
           console.info('←', res.status(), res.url())
         );

         await page.goto('/communaute', { waitUntil: 'networkidle' });

         await page.waitForResponse(
           (res) =>
             res.url().includes('/api/chat/threads') && res.status() === 200
         );

         const button = await page.getByRole('button', { name: 'Fil principal' });
         await expect(button).toBeVisible();

         await button.click();
         await expect(
           page.getByText('Bienvenue sur le fil !', { exact: false })
         ).toBeVisible();
       });
     });