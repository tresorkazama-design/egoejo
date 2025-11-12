const { test, expect } = require("@playwright/test");

const THREADS_FIXTURE = [
  {
    id: 1,
    title: "Fil principal",
    participants: [{ username: "Alice" }, { username: "Bob" }],
    last_message_at: new Date().toISOString(),
  },
];

const THREAD_DETAIL_FIXTURE = {
  id: 1,
  title: "Fil principal",
  participants: [{ username: "Alice" }, { username: "Bob" }],
};

const MESSAGES_FIXTURE = [
  {
    id: 100,
    content: "Bienvenue sur le fil !",
    author: { username: "Alice" },
    created_at: new Date().toISOString(),
  },
];

test.describe("Page CommunautÃ©", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/**", async (route) => {
      const request = route.request();
      const url = new URL(request.url());
      const pathname = url.pathname;
      const method = request.method();

      if (pathname.endsWith("/api/chat/threads/") && method === "GET") {
        await route.fulfill({
          status: 200,
          body: JSON.stringify(THREADS_FIXTURE),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      if (pathname.endsWith("/api/chat/threads/1/") && method === "GET") {
        await route.fulfill({
          status: 200,
          body: JSON.stringify(THREAD_DETAIL_FIXTURE),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      if (pathname.endsWith("/api/chat/messages/") && method === "GET") {
        const threadId = url.searchParams.get("thread");
        const payload = threadId === "1" ? MESSAGES_FIXTURE : [];
        await route.fulfill({
          status: 200,
          body: JSON.stringify(payload),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      if (pathname.endsWith("/api/chat/messages/") && method === "POST") {
        await route.fulfill({
          status: 201,
          body: JSON.stringify({
            id: 999,
            content: JSON.parse(request.postData() || "{}" ).content || "",
            author: { username: "Vous" },
            created_at: new Date().toISOString(),
          }),
          headers: { "Content-Type": "application/json" },
        });
        return;
      }

      await route.continue();
    });

    await page.route("**/ws/**", (route) => route.abort());
  });

  test("affiche les fils et permet de sÃ©lectionner un fil", async ({ page }) => {
    await page.goto("/communaute");
    await page.waitForLoadState("networkidle");
    await page.waitForSelector(".page-loading", { state: "detached", timeout: 10000 }).catch(() => {});
    const heading = page.locator("h1", { hasText: "Echanges en temps" });
    await expect(heading).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole("button", { name: "Fil principal" })).toBeVisible({ timeout: 10000 });

    await page.getByRole("button", { name: "Fil principal" }).click();
    await expect(page.getByText("Bienvenue sur le fil !")).toBeVisible({ timeout: 10000 });
  });
});
