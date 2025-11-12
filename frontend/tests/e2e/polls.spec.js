const { test, expect } = require("@playwright/test");

const POLL_SUMMARY_FIXTURE = [
  {
    id: 1,
    title: "Choix du lieu",
    question: "OÃ¹ allons-nous ?",
    status: "open",
    total_votes: 3,
  },
];

const POLL_DETAIL_FIXTURE = {
  id: 1,
  title: "Choix du lieu",
  question: "OÃ¹ allons-nous ?",
  status: "open",
  total_votes: 3,
  allow_multiple: false,
  is_anonymous: true,
  options: [
    { id: 10, label: "Montagne", votes: 2 },
    { id: 11, label: "Mer", votes: 1 },
  ],
};

const POLL_VOTE_RESPONSE = {
  ...POLL_DETAIL_FIXTURE,
  total_votes: 4,
  options: [
    { id: 10, label: "Montagne", votes: 3 },
    { id: 11, label: "Mer", votes: 1 },
  ],
};

test.describe("Page Votes", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/**", async (route) => {
      const request = route.request();
      const url = new URL(request.url());
      const pathname = url.pathname;
      const method = request.method();

      if (pathname.endsWith("/api/polls/") && method === "GET") {
        await route.fulfill({
          status: 200,
          body: JSON.stringify(POLL_SUMMARY_FIXTURE),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      if (pathname.endsWith("/api/polls/1/") && method === "GET") {
        await route.fulfill({
          status: 200,
          body: JSON.stringify(POLL_DETAIL_FIXTURE),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      if (pathname.endsWith("/api/polls/1/vote/") && method === "POST") {
        await route.fulfill({
          status: 200,
          body: JSON.stringify(POLL_VOTE_RESPONSE),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      if (pathname.match(/\/api\/polls\/\d+\/(open|close)\//) && method === "POST") {
        await route.fulfill({
          status: 200,
          body: JSON.stringify(POLL_DETAIL_FIXTURE),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      await route.continue();
    });

    await page.route("**/ws/**", (route) => route.abort());
  });

  test("affiche les scrutins et permet de voter", async ({ page }) => {
    await page.goto("/votes");
    await page.waitForLoadState("networkidle");
    await page.waitForSelector(".page-loading", { state: "detached", timeout: 10000 }).catch(() => {});
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({ timeout: 10000 });

    const pollButton = page.getByRole("button", { name: "Choix du lieu" });
    await expect(pollButton).toBeVisible({ timeout: 10000 });
    await pollButton.click();

    await expect(page.getByRole("heading", { level: 2, name: "Choix du lieu" })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("OÃ¹ allons-nous ?")).toBeVisible({ timeout: 10000 });

    await page.waitForSelector("input[type=radio][value='10']", { timeout: 10000 });
    await page.getByRole("radio", { name: "Montagne" }).check();
    await page.getByRole("button", { name: "Voter" }).click();
    await expect(page.getByText("Montagne", { exact: false })).toBeVisible({ timeout: 10000 });
  });
});
