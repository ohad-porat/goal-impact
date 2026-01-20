import { test, expect, Page } from "@playwright/test";
import {
  navigateAndWait,
  getFilteredTableRows,
  verifyEmptyStateOrContent,
  verifyTableHeaders,
} from "./helpers";

async function verifyClickableLinks(
  page: Page,
  linkSelector: string,
  hrefPattern: RegExp,
) {
  const links = page.locator(linkSelector);
  const count = await links.count();

  expect(count).toBeGreaterThan(0);

  const firstLink = links.first();
  const href = await firstLink.getAttribute("href");
  expect(href).toMatch(hrefPattern);
}

function getNationRows(page: Page) {
  return getFilteredTableRows(page, "No nations found");
}

async function getFirstNationLink(page: Page) {
  const rows = getNationRows(page);
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);
  return rows.first().getByRole("link").first();
}

test.describe("Nations", () => {
  test.describe("List Page", () => {
    test.beforeEach(async ({ page }) => {
      await navigateAndWait(page, "/nations");
    });

    test("should display nations page heading", async ({ page }) => {
      await expect(
        page.getByRole("heading", { name: "Nations" }),
      ).toBeVisible();
    });

    test("should display nations table with headers", async ({ page }) => {
      await verifyTableHeaders(page, [
        "Nation",
        "FIFA Code",
        "Governing Body",
        "Players",
      ]);
    });

    test("should display nations in table with clickable links", async ({
      page,
    }) => {
      const rows = getNationRows(page);
      const count = await rows.count();

      expect(count).toBeGreaterThan(0);

      const firstRow = rows.first();
      const nationLink = firstRow.getByRole("link").first();
      await expect(nationLink).toBeVisible();

      const rowText = await firstRow.textContent();
      expect(rowText).toBeTruthy();

      const href = await nationLink.getAttribute("href");
      expect(href).toMatch(/^\/nations\/\d+$/);
    });

    test("should handle empty state when no nations", async ({ page }) => {
      const rows = getNationRows(page);
      await verifyEmptyStateOrContent(page, "No nations found", rows);
    });
  });

  test.describe("Detail Page", () => {
    let nationId: number | null = null;

    test.beforeEach(async ({ page }) => {
      await navigateAndWait(page, "/nations");

      const nationLink = await getFirstNationLink(page);
      expect(nationLink).not.toBeNull();

      const href = await nationLink!.getAttribute("href");
      expect(href).toBeTruthy();

      const match = href!.match(/\/nations\/(\d+)/);
      expect(match).toBeTruthy();

      nationId = parseInt(match![1]);
      await nationLink!.click();
      await page.waitForLoadState("networkidle");
    });

    test("should navigate from list to detail page", async ({ page }) => {
      expect(nationId).not.toBeNull();
      await expect(page).toHaveURL(`/nations/${nationId}`);
    });

    test("should display nation name and details", async ({ page }) => {
      expect(nationId).not.toBeNull();

      const heading = page
        .getByRole("heading", { name: /^[A-Za-z\s]+$/ })
        .first();
      await expect(heading).toBeVisible();

      const fifaCodeText = page.getByText(/FIFA Code:/);
      await expect(fifaCodeText).toBeVisible();

      const governingBodyText = page.getByText(/Governing Body:/);
      await expect(governingBodyText).toBeVisible();
    });

    test.describe("Competitions List", () => {
      test("should display competitions section", async ({ page }) => {
        expect(nationId).not.toBeNull();
        await expect(
          page.getByRole("heading", { name: "Leagues" }),
        ).toBeVisible();
      });

      test("should display competitions list with clickable links", async ({
        page,
      }) => {
        expect(nationId).not.toBeNull();

        const competitionRows = getFilteredTableRows(page, "No leagues found.");
        const rowCount = await competitionRows.count();

        expect(rowCount).toBeGreaterThan(0);

        await page.waitForSelector('a[href^="/leagues/"]', {
          state: "visible",
          timeout: 5000,
        });

        await verifyClickableLinks(
          page,
          'a[href^="/leagues/"]',
          /^\/leagues\/\d+$/,
        );
      });
    });

    test.describe("Clubs Table", () => {
      test("should display clubs section", async ({ page }) => {
        expect(nationId).not.toBeNull();
        await expect(
          page.getByRole("heading", { name: "Top Clubs" }),
        ).toBeVisible();
      });

      test("should display clubs table with headers", async ({ page }) => {
        expect(nationId).not.toBeNull();
        await verifyTableHeaders(page, ["Club", "Avg Pos"]);
      });

      test("should display clubs with clickable links", async ({ page }) => {
        expect(nationId).not.toBeNull();

        const clubRows = getFilteredTableRows(
          page,
          "No qualifying clubs found.",
        );
        const rowCount = await clubRows.count();

        expect(rowCount).toBeGreaterThan(0);

        await page.waitForSelector('a[href^="/clubs/"]', {
          state: "visible",
          timeout: 5000,
        });

        await verifyClickableLinks(
          page,
          'a[href^="/clubs/"]',
          /^\/clubs\/\d+$/,
        );
      });

      test("should display average position for clubs", async ({ page }) => {
        expect(nationId).not.toBeNull();

        const clubRows = getFilteredTableRows(
          page,
          "No qualifying clubs found.",
        );
        const count = await clubRows.count();

        expect(count).toBeGreaterThan(0);

        const firstRow = clubRows.first();
        const rowText = await firstRow.textContent();
        expect(rowText).toBeTruthy();
        expect(rowText).toMatch(/\d+/);
      });
    });

    test.describe("Players Table", () => {
      test("should display players section", async ({ page }) => {
        expect(nationId).not.toBeNull();
        await expect(
          page.getByRole("heading", { name: "Top Players" }),
        ).toBeVisible();
      });

      test("should display players table with headers", async ({ page }) => {
        expect(nationId).not.toBeNull();
        await verifyTableHeaders(page, ["Player", "Career GV"]);
      });

      test("should display players or empty state with clickable links", async ({
        page,
      }) => {
        expect(nationId).not.toBeNull();

        const playerRows = getFilteredTableRows(page, "No players found.");
        const rowCount = await playerRows.count();
        const emptyState = page.getByText("No players found.");
        const hasEmptyState = await emptyState.isVisible().catch(() => false);

        if (hasEmptyState) {
          await expect(emptyState).toBeVisible();
        } else {
          expect(rowCount).toBeGreaterThan(0);
          await page.waitForSelector('a[href^="/players/"]', {
            state: "visible",
            timeout: 5000,
          });
          await verifyClickableLinks(
            page,
            'a[href^="/players/"]',
            /^\/players\/\d+$/,
          );
        }
      });

      test("should display career goal value for players", async ({ page }) => {
        expect(nationId).not.toBeNull();

        const playerRows = getFilteredTableRows(page, "No players found.");
        const count = await playerRows.count();

        expect(count).toBeGreaterThan(0);

        const firstRow = playerRows.first();
        const rowText = await firstRow.textContent();
        expect(rowText).toBeTruthy();
        expect(rowText).toMatch(/\d+\.?\d*/);
      });
    });
  });

  test.describe("Navigation Flow", () => {
    test("should navigate from list to detail and back", async ({ page }) => {
      await navigateAndWait(page, "/nations");

      const nationLink = await getFirstNationLink(page);
      expect(nationLink).not.toBeNull();

      const nationName = await nationLink!.textContent();
      expect(nationName).toBeTruthy();

      await nationLink!.click();
      await page.waitForLoadState("networkidle");

      const heading = page.getByRole("heading", { name: nationName!.trim() });
      await expect(heading).toBeVisible();

      await page.goBack();
      await page.waitForLoadState("networkidle");

      await expect(page).toHaveURL("/nations");
      await expect(
        page.getByRole("heading", { name: "Nations" }),
      ).toBeVisible();
    });

    test("should navigate from detail to linked pages", async ({ page }) => {
      await navigateAndWait(page, "/nations");

      const nationLink = await getFirstNationLink(page);
      expect(nationLink).not.toBeNull();

      await nationLink!.click();
      await page.waitForLoadState("networkidle");
      await expect(page).toHaveURL(/\/nations\/\d+$/);

      const leaguesSection = page.locator('h2:has-text("Leagues")');
      await expect(leaguesSection).toBeVisible({ timeout: 5000 });

      const competitionLinks = page.locator('a[href^="/leagues/"]');
      await expect(competitionLinks.first()).toBeVisible({ timeout: 5000 });
      const competitionCount = await competitionLinks.count();
      expect(competitionCount).toBeGreaterThan(0);

      await competitionLinks.first().click();
      await page.waitForLoadState("networkidle");
      await expect(page).toHaveURL(/\/leagues\/\d+/);
    });
  });
});
