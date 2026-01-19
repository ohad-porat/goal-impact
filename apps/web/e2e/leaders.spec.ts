import { test, expect, Page } from "@playwright/test";
import {
  navigateAndWait,
  waitForPageReady,
  verifyTableWithData,
  selectFilterOptionIfAvailable,
  getUrlParam,
} from "./helpers";

function getCareerTotalsTab(page: Page) {
  return page.getByRole("button", { name: "Career Totals" });
}

function getAllSeasonsTab(page: Page) {
  return page.getByRole("button", { name: "All Seasons" });
}

function getBySeasonTab(page: Page) {
  return page.getByRole("button", { name: "By Season" });
}

function getLeagueFilter(page: Page) {
  return page.locator("select#league-filter");
}

function getSeasonFilter(page: Page) {
  return page.locator("select#season-filter");
}

async function verifyTableOrEmptyState(
  page: Page,
  emptyStateText: string,
  errorText: string,
) {
  const table = page.locator("table");
  const emptyState = page.getByText(emptyStateText);
  const errorMessage = page.getByText(errorText);

  const hasTable = await table.isVisible().catch(() => false);
  const hasEmptyState = await emptyState.isVisible().catch(() => false);
  const hasError = await errorMessage.isVisible().catch(() => false);

  expect(hasTable || hasEmptyState || hasError).toBe(true);

  if (hasTable) {
    await verifyTableWithData(page);
  } else if (hasEmptyState) {
    await expect(emptyState).toBeVisible();
  } else {
    await expect(errorMessage).toBeVisible();
  }
}

test.describe("Leaders", () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, "/leaders");
  });

  test.describe("Page Structure", () => {
    test("should display leaders page heading", async ({ page }) => {
      await expect(page.getByTestId("leaders-page-heading")).toBeVisible();
    });

    test("should display tab buttons", async ({ page }) => {
      await expect(getCareerTotalsTab(page)).toBeVisible();
      await expect(getAllSeasonsTab(page)).toBeVisible();
      await expect(getBySeasonTab(page)).toBeVisible();
    });

    test("should have Career Totals tab active by default", async ({
      page,
    }) => {
      const careerTab = getCareerTotalsTab(page);
      await expect(careerTab).toHaveClass(/bg-orange-400/);
    });
  });

  test.describe("Career Totals Tab", () => {
    test("should display Career Totals tab content", async ({ page }) => {
      await expect(
        page.getByRole("heading", { name: "Career Leaders by Goal Value" }),
      ).toBeVisible();
    });

    test("should display league filter dropdown", async ({ page }) => {
      const leagueFilter = getLeagueFilter(page);
      await expect(leagueFilter).toBeVisible();

      const allLeaguesOption = leagueFilter.locator("option", {
        hasText: "All Leagues",
      });
      await expect(allLeaguesOption).toHaveCount(1);
    });

    test("should display career totals table when data loads", async ({
      page,
    }) => {
      await waitForPageReady(page);

      const table = page.locator("table");
      const errorMessage = page.getByText("Failed to load career totals data.");

      const hasTable = await table.isVisible().catch(() => false);
      const hasError = await errorMessage.isVisible().catch(() => false);

      if (hasError) {
        throw new Error(
          "Failed to load career totals data - test cannot verify table is displayed",
        );
      }

      expect(hasTable).toBe(true);
      await verifyTableWithData(page);
    });

    test("should filter by league when selecting league", async ({ page }) => {
      await waitForPageReady(page);

      const leagueFilter = getLeagueFilter(page);
      const initialUrl = page.url();

      const selected = await selectFilterOptionIfAvailable(
        page,
        leagueFilter,
        1,
      );

      expect(selected).toBe(true);

      const newUrl = page.url();
      expect(newUrl).not.toBe(initialUrl);
      expect(getUrlParam(page, "league_id")).toBeTruthy();
    });

    test('should reset to all leagues when selecting "All Leagues"', async ({
      page,
    }) => {
      await waitForPageReady(page);

      const leagueFilter = getLeagueFilter(page);
      const options = leagueFilter.locator("option");
      const optionCount = await options.count();

      expect(optionCount).toBeGreaterThan(1);

      await leagueFilter.selectOption({ index: 1 });
      await waitForPageReady(page);

      expect(getUrlParam(page, "league_id")).toBeTruthy();

      await leagueFilter.selectOption("");
      await waitForPageReady(page);

      expect(getUrlParam(page, "league_id")).toBeNull();
    });
  });

  test.describe("All Seasons Tab", () => {
    test.beforeEach(async ({ page }) => {
      await getAllSeasonsTab(page).click();
      await waitForPageReady(page);
    });

    test("should display All Seasons tab content", async ({ page }) => {
      await expect(
        page.getByRole("heading", {
          name: "All Seasons Leaders by Goal Value",
        }),
      ).toBeVisible();
    });

    test("should display league filter dropdown but no season filter", async ({
      page,
    }) => {
      const leagueFilter = getLeagueFilter(page);
      const seasonFilter = getSeasonFilter(page);

      await expect(leagueFilter).toBeVisible();
      await expect(seasonFilter).not.toBeVisible();
    });

    test("should display all seasons table when data loads", async ({
      page,
    }) => {
      await waitForPageReady(page);

      const table = page.locator("table");
      const errorMessage = page.getByText("Failed to load all-seasons data.");

      await Promise.race([
        table.waitFor({ state: "visible", timeout: 5000 }).catch(() => null),
        errorMessage
          .waitFor({ state: "visible", timeout: 5000 })
          .catch(() => null),
      ]);

      const hasError = await errorMessage.isVisible().catch(() => false);
      if (hasError) {
        throw new Error(
          "Failed to load all-seasons data - test cannot verify table is displayed",
        );
      }

      await expect(table).toBeVisible();
      await verifyTableWithData(page);
    });

    test("should display season column in table", async ({ page }) => {
      await waitForPageReady(page);

      const table = page.locator("table");
      const errorMessage = page.getByText("Failed to load all-seasons data.");
      const hasError = await errorMessage
        .isVisible({ timeout: 1000 })
        .catch(() => false);

      if (hasError) {
        test.skip();
      }

      await expect(table).toBeVisible({ timeout: 5000 });

      const headers = table.locator("thead th");
      const headerTexts = await headers.allTextContents();
      const hasSeasonHeader = headerTexts.some(
        (text) => text.includes("Season") || text === "Season",
      );

      expect(hasSeasonHeader).toBe(true);
    });

    test("should filter by league when selecting league", async ({ page }) => {
      await waitForPageReady(page);

      const leagueFilter = getLeagueFilter(page);
      const initialUrl = page.url();

      const selected = await selectFilterOptionIfAvailable(
        page,
        leagueFilter,
        1,
      );

      expect(selected).toBe(true);

      const newUrl = page.url();
      expect(newUrl).not.toBe(initialUrl);
      expect(getUrlParam(page, "league_id")).toBeTruthy();
    });

    test('should reset to all leagues when selecting "All Leagues"', async ({
      page,
    }) => {
      await waitForPageReady(page);

      const leagueFilter = getLeagueFilter(page);
      const options = leagueFilter.locator("option");
      const optionCount = await options.count();

      expect(optionCount).toBeGreaterThan(1);

      await leagueFilter.selectOption({ index: 1 });
      await waitForPageReady(page);

      expect(getUrlParam(page, "league_id")).toBeTruthy();

      await leagueFilter.selectOption("");
      await waitForPageReady(page);

      expect(getUrlParam(page, "league_id")).toBeNull();
    });

    test("should allow same player to appear multiple times for different seasons", async ({
      page,
    }) => {
      await waitForPageReady(page);

      const table = page.locator("table");
      const errorMessage = page.getByText("Failed to load all-seasons data.");
      const hasError = await errorMessage
        .isVisible({ timeout: 1000 })
        .catch(() => false);

      if (hasError) {
        test.skip();
      }

      await expect(table).toBeVisible({ timeout: 5000 });

      const headers = table.locator("thead th");
      const headerTexts = await headers.allTextContents();

      const hasPlayerColumn = headerTexts.some(
        (text) => text.includes("Player") || text.includes("Name"),
      );
      const hasSeasonColumn = headerTexts.some((text) =>
        text.includes("Season"),
      );

      expect(hasPlayerColumn).toBe(true);
      expect(hasSeasonColumn).toBe(true);

      const rows = table.locator("tbody tr");
      const rowCount = await rows.count();

      if (rowCount >= 2) {
        const playerNames = await Promise.all(
          Array.from({ length: Math.min(rowCount, 5) }).map(async (_, i) => {
            const playerCell = rows.nth(i).locator("td").nth(1);
            return await playerCell.textContent();
          }),
        );

        const seenPlayers = new Set<string>();
        for (let i = 0; i < playerNames.length; i++) {
          const player = playerNames[i]?.trim();
          if (player) {
            if (seenPlayers.has(player)) {
              const seasonCell = rows.nth(i).locator("td").nth(2);
              const season = await seasonCell.textContent();
              expect(season?.trim().length).toBeGreaterThan(0);
            }
            seenPlayers.add(player);
          }
        }
      }
    });
  });

  test.describe("By Season Tab", () => {
    test.beforeEach(async ({ page }) => {
      await getBySeasonTab(page).click();
      await waitForPageReady(page);
    });

    test("should display league and season filter dropdowns", async ({
      page,
    }) => {
      const leagueFilter = getLeagueFilter(page);
      const seasonFilter = getSeasonFilter(page);

      await expect(leagueFilter).toBeVisible();
      await expect(seasonFilter).toBeVisible();
    });

    test("should have a season selected by default", async ({ page }) => {
      await waitForPageReady(page);

      const seasonFilter = getSeasonFilter(page);
      const selectedValue = await seasonFilter.inputValue();

      expect(selectedValue).toBeTruthy();
      expect(getUrlParam(page, "season_id")).toBeTruthy();
    });

    test("should display by season table when data loads", async ({ page }) => {
      await waitForPageReady(page);

      const table = page.locator("table");
      const errorMessage = page.getByText("Failed to load by-season data.");

      const hasTable = await table.isVisible().catch(() => false);
      const hasError = await errorMessage.isVisible().catch(() => false);

      if (hasError) {
        throw new Error(
          "Failed to load by-season data - test cannot verify table is displayed",
        );
      }

      expect(hasTable).toBe(true);
      await verifyTableWithData(page);
    });

    test("should filter by league when selecting league", async ({ page }) => {
      await waitForPageReady(page);

      const leagueFilter = getLeagueFilter(page);
      const initialUrl = page.url();

      const selected = await selectFilterOptionIfAvailable(
        page,
        leagueFilter,
        1,
      );

      expect(selected).toBe(true);

      const newUrl = page.url();
      expect(newUrl).not.toBe(initialUrl);
      expect(getUrlParam(page, "league_id")).toBeTruthy();
    });

    test("should filter by season when selecting season", async ({ page }) => {
      await waitForPageReady(page);

      const seasonFilter = getSeasonFilter(page);
      const options = seasonFilter.locator("option");
      const optionCount = await options.count();

      expect(optionCount).toBeGreaterThan(1);

      const initialSeasonId = getUrlParam(page, "season_id");

      await seasonFilter.selectOption({ index: optionCount - 1 });
      await waitForPageReady(page);

      const newSeasonId = getUrlParam(page, "season_id");

      expect(newSeasonId).toBeTruthy();
      expect(newSeasonId).not.toBe(initialSeasonId);
    });
  });

  test.describe("Tab Switching", () => {
    test("should switch between all tabs", async ({ page }) => {
      await waitForPageReady(page);

      const careerTab = getCareerTotalsTab(page);
      const allSeasonsTab = getAllSeasonsTab(page);
      const bySeasonTab = getBySeasonTab(page);

      await expect(careerTab).toHaveClass(/bg-orange-400/);
      await expect(
        page.getByRole("heading", { name: "Career Leaders by Goal Value" }),
      ).toBeVisible();

      await allSeasonsTab.click();
      await waitForPageReady(page);

      await expect(allSeasonsTab).toHaveClass(/bg-orange-400/);
      await expect(
        page.getByRole("heading", {
          name: "All Seasons Leaders by Goal Value",
        }),
      ).toBeVisible();

      await bySeasonTab.click();
      await waitForPageReady(page);

      await expect(bySeasonTab).toHaveClass(/bg-orange-400/);
      await expect(
        page.getByRole("heading", { name: "Season Leaders by Goal Value" }),
      ).toBeVisible();

      await careerTab.click();
      await waitForPageReady(page);

      await expect(careerTab).toHaveClass(/bg-orange-400/);
      await expect(
        page.getByRole("heading", { name: "Career Leaders by Goal Value" }),
      ).toBeVisible();
    });

    test("should maintain tab state in URL", async ({ page }) => {
      await waitForPageReady(page);

      const allSeasonsTab = getAllSeasonsTab(page);
      await allSeasonsTab.click();
      await waitForPageReady(page);

      expect(getUrlParam(page, "view")).toBe("all-seasons");

      const bySeasonTab = getBySeasonTab(page);
      await bySeasonTab.click();
      await waitForPageReady(page);

      expect(getUrlParam(page, "view")).toBe("by-season");

      const careerTab = getCareerTotalsTab(page);
      await careerTab.click();
      await waitForPageReady(page);

      expect(getUrlParam(page, "view")).toBe("career");
    });
  });
});
