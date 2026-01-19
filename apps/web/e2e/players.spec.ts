import { test, expect, Page } from "@playwright/test";
import {
  navigateAndWait,
  getSeasonSelector,
  verifyTableWithData,
  navigateToGoalLog,
} from "./helpers";

async function hasNoGoals(
  page: Page,
  emptyStateText: string = "No goals found for this player",
): Promise<boolean> {
  const noGoalsText = page.getByText(emptyStateText);
  return await noGoalsText.isVisible().catch(() => false);
}

async function navigateToPlayerViaSearch(
  page: Page,
  searchQuery: string = "test",
): Promise<number> {
  await navigateAndWait(page, "/");

  const searchInput = page.getByPlaceholder("Search...");
  await searchInput.fill(searchQuery);
  await page
    .waitForSelector("text=Searching...", { state: "hidden", timeout: 5000 })
    .catch(() => {});
  await page.waitForTimeout(300);

  const resultsDropdown = page.locator('[class*="bg-slate-700"]').filter({
    hasText: /Player|Club|Competition|Nation|No results found/,
  });
  await expect(resultsDropdown).toBeVisible({ timeout: 5000 });

  const playerResults = page.locator("button").filter({ hasText: /Player/ });
  const count = await playerResults.count();
  expect(count).toBeGreaterThan(0);

  const player1Result = playerResults.filter({ hasText: "Test Player 1" });
  const player1Count = await player1Result.count();
  if (player1Count > 0) {
    await player1Result.first().click();
  } else {
    await playerResults.first().click();
  }
  await page.waitForURL(/\/players\/\d+/, { timeout: 5000 });
  await page.waitForLoadState("networkidle");

  const url = page.url();
  const match = url.match(/\/players\/(\d+)/);
  expect(match).toBeTruthy();

  return parseInt(match![1]);
}

test.describe("Players", () => {
  test.describe("Detail Page", () => {
    let playerId: number | null = null;

    test.beforeEach(async ({ page }) => {
      playerId = await navigateToPlayerViaSearch(page);
    });

    test("should navigate to player detail page", async ({ page }) => {
      expect(playerId).not.toBeNull();
      await expect(page).toHaveURL(`/players/${playerId}`);
    });

    test("should display player name", async ({ page }) => {
      expect(playerId).not.toBeNull();

      const heading = page.getByRole("heading", { level: 1 });
      await expect(heading).toBeVisible();

      const headingText = await heading.textContent();
      expect(headingText).toBeTruthy();
      expect(headingText?.trim().length).toBeGreaterThan(0);
    });

    test("should display player nation if available", async ({ page }) => {
      expect(playerId).not.toBeNull();

      const countryText = page.getByText(/Country:/);
      const isVisible = await countryText.isVisible().catch(() => false);

      if (isVisible) {
        await expect(countryText).toBeVisible();
        const countrySection = page.locator("text=/Country:/").locator("..");
        const countryValue = await countrySection.textContent();
        expect(countryValue).toBeTruthy();
        expect(countryValue?.trim().length).toBeGreaterThan("Country:".length);
      }
    });

    test('should display "View Goal Log" button', async ({ page }) => {
      expect(playerId).not.toBeNull();

      const goalLogButton = page.getByRole("link", { name: "View Goal Log" });
      await expect(goalLogButton).toBeVisible();

      const href = await goalLogButton.getAttribute("href");
      expect(href).toBe(`/players/${playerId}/goals`);
    });

    test("should display seasons table with data", async ({ page }) => {
      expect(playerId).not.toBeNull();
      await verifyTableWithData(page);
    });
  });

  test.describe("Goal Log Page", () => {
    let playerId: number | null = null;

    test.beforeEach(async ({ page }) => {
      playerId = await navigateToPlayerViaSearch(page);
      expect(playerId).not.toBeNull();
      await navigateToGoalLog(page);
    });

    test("should navigate from detail to goal log", async ({ page }) => {
      expect(playerId).not.toBeNull();
      await expect(page).toHaveURL(
        new RegExp(`/players/${playerId}/goals(\\?season=\\d+)?$`),
      );
    });

    test("should display goal log heading", async ({ page }) => {
      expect(playerId).not.toBeNull();
      await expect(page).toHaveURL(
        new RegExp(`/players/${playerId}/goals\\?season=\\d+$`),
      );

      const heading = page.getByRole("heading", { level: 1 });
      await expect(heading).toBeVisible();

      const headingText = await heading.textContent();
      expect(headingText).toBeTruthy();
      expect(headingText).toContain("Goal Log");
    });

    test('should display "Back to Player" button', async ({ page }) => {
      expect(playerId).not.toBeNull();

      const backButton = page.getByRole("link", { name: "Back to Player" });
      await expect(backButton).toBeVisible();

      const href = await backButton.getAttribute("href");
      expect(href).toBe(`/players/${playerId}`);
    });

    test('should navigate back to player when clicking "Back to Player"', async ({
      page,
    }) => {
      expect(playerId).not.toBeNull();

      const backButton = page.getByRole("link", { name: "Back to Player" });
      await backButton.click();
      await page.waitForLoadState("networkidle");

      await expect(page).toHaveURL(`/players/${playerId}`);
    });

    test("should display season selector when goals exist", async ({
      page,
    }) => {
      expect(playerId).not.toBeNull();

      const hasNoGoalsState = await hasNoGoals(page);
      expect(hasNoGoalsState).toBe(false);

      const seasonSelector = getSeasonSelector(page);
      await expect(seasonSelector).toBeVisible();
    });

    test("should display goal log table when goals exist", async ({ page }) => {
      expect(playerId).not.toBeNull();

      const hasNoGoalsState = await hasNoGoals(page);
      expect(hasNoGoalsState).toBe(false);

      await verifyTableWithData(page);
    });

    test("should handle empty state when no goals", async ({ page }) => {
      expect(playerId).not.toBeNull();
      await expect(page).toHaveURL(
        new RegExp(`/players/${playerId}/goals(\\?season=\\d+)?$`),
      );

      const hasNoGoalsState = await hasNoGoals(page);
      if (hasNoGoalsState) {
        const noGoalsText = page.getByText("No goals found for this player");
        await expect(noGoalsText).toBeVisible();
      } else {
        const goalLogTable = page.locator("table");
        await expect(goalLogTable).toBeVisible();
      }
    });

    test.describe("Season Selector", () => {
      test("should have seasons available", async ({ page }) => {
        expect(playerId).not.toBeNull();
        await expect(page).toHaveURL(
          new RegExp(`/players/${playerId}/goals\\?season=\\d+$`),
        );

        const hasNoGoalsState = await hasNoGoals(page);
        expect(hasNoGoalsState).toBe(false);

        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();
        const options = seasonSelector.locator("option");
        const optionCount = await options.count();

        expect(optionCount).toBeGreaterThan(0);
      });

      test("should change season when selecting different option", async ({
        page,
      }) => {
        expect(playerId).not.toBeNull();
        await expect(page).toHaveURL(
          new RegExp(`/players/${playerId}/goals\\?season=\\d+$`),
        );

        const hasNoGoalsState = await hasNoGoals(page);
        expect(hasNoGoalsState).toBe(false);

        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();

        const options = seasonSelector.locator("option");
        const optionCount = await options.count();

        expect(optionCount).toBeGreaterThan(1);

        const lastOptionValue = await options
          .nth(optionCount - 1)
          .getAttribute("value");
        expect(lastOptionValue).toBeTruthy();

        const initialUrl = page.url();
        await seasonSelector.selectOption(lastOptionValue!);
        await page.waitForURL(
          new RegExp(`/players/${playerId}/goals\\?season=${lastOptionValue}`),
          { timeout: 5000 },
        );
        await page.waitForLoadState("networkidle");

        const newUrl = page.url();
        expect(newUrl).not.toBe(initialUrl);
        expect(newUrl).toContain(`season=${lastOptionValue}`);
      });

      test("should update goal log table when season changes", async ({
        page,
      }) => {
        expect(playerId).not.toBeNull();
        await expect(page).toHaveURL(
          new RegExp(`/players/${playerId}/goals\\?season=\\d+$`),
        );

        const hasNoGoalsState = await hasNoGoals(page);
        expect(hasNoGoalsState).toBe(false);

        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();

        const options = seasonSelector.locator("option");
        const optionCount = await options.count();

        expect(optionCount).toBeGreaterThan(1);

        const tableRows = page.locator("tbody tr");
        const initialRowCount = await tableRows.count();

        expect(initialRowCount).toBeGreaterThan(0);

        const initialFirstRowText = await tableRows.first().textContent();

        const lastOptionValue = await options
          .nth(optionCount - 1)
          .getAttribute("value");
        expect(lastOptionValue).toBeTruthy();

        await seasonSelector.selectOption(lastOptionValue!);
        await page.waitForURL(
          new RegExp(`/players/${playerId}/goals\\?season=${lastOptionValue}`),
          { timeout: 5000 },
        );
        await page.waitForLoadState("networkidle");

        const newTableRows = page.locator("tbody tr");
        const newRowCount = await newTableRows.count();
        const newFirstRowText = await newTableRows.first().textContent();

        expect(newRowCount).toBeGreaterThan(0);

        if (initialRowCount === newRowCount) {
          expect(newFirstRowText).not.toBe(initialFirstRowText);
        } else {
          expect(newRowCount).not.toBe(initialRowCount);
        }
      });

      test("should include season parameter in URL", async ({ page }) => {
        expect(playerId).not.toBeNull();

        const hasNoGoalsState = await hasNoGoals(page);
        expect(hasNoGoalsState).toBe(false);

        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();
        const options = seasonSelector.locator("option");
        const optionCount = await options.count();

        expect(optionCount).toBeGreaterThan(0);

        const firstOptionValue = await options.first().getAttribute("value");
        expect(firstOptionValue).toBeTruthy();
        expect(page.url()).toContain(`season=${firstOptionValue}`);
      });
    });
  });
});
