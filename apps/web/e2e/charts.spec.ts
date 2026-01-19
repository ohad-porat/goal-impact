import { test, expect, Page } from "@playwright/test";
import {
  navigateAndWait,
  waitForPageReady,
  selectFilterOptionIfAvailable,
  getUrlParam,
  checkForChartError,
} from "./helpers";

function getLeagueFilter(page: Page) {
  return page.locator("select#league-filter");
}

async function verifyChartRenders(page: Page) {
  const chartTitle = page.getByRole("heading", {
    name: "Career Totals Scatter Chart",
  });
  await expect(chartTitle).toBeVisible();

  const emptyState = page.getByText(
    "No data available for the selected league.",
  );
  const hasEmptyState = await emptyState.isVisible().catch(() => false);

  if (hasEmptyState) {
    await expect(emptyState).toBeVisible();
    return;
  }

  const chartContainer = page.getByTestId("career-totals-scatter-chart");
  await expect(chartContainer).toBeVisible({ timeout: 5000 });

  const scatterChart = chartContainer.locator("svg").first();
  await expect(scatterChart).toBeVisible({ timeout: 5000 });

  const axisLabels = page
    .locator("text")
    .filter({ hasText: /Total Goals|Total Goal Value/ });
  const axisLabelCount = await axisLabels.count();
  if (axisLabelCount > 0) {
    await expect(axisLabels.first()).toBeVisible({ timeout: 2000 });
  }
}

test.describe("Charts", () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, "/charts");
  });

  test.describe("Chart Rendering", () => {
    test("should render scatter chart when data loads", async ({ page }) => {
      await waitForPageReady(page, 3000);

      const hasError = await checkForChartError(page);
      if (hasError) {
        throw new Error(
          "Failed to load chart data - test cannot verify chart is displayed",
        );
      }

      await verifyChartRenders(page);
    });
  });

  test.describe("League Filtering", () => {
    test("should filter by league when selecting league", async ({ page }) => {
      await waitForPageReady(page, 3000);

      const leagueFilter = getLeagueFilter(page);
      const initialUrl = page.url();

      const options = leagueFilter.locator("option");
      const optionCount = await options.count();

      expect(optionCount).toBeGreaterThan(1);

      const selected = await selectFilterOptionIfAvailable(
        page,
        leagueFilter,
        1,
      );

      expect(selected).toBe(true);

      const newUrl = page.url();
      expect(newUrl).not.toBe(initialUrl);
      expect(getUrlParam(page, "league_id")).toBeTruthy();

      await waitForPageReady(page, 2000);
      await verifyChartRenders(page);
    });

    test('should reset to all leagues when selecting "All Leagues"', async ({
      page,
    }) => {
      await waitForPageReady(page, 3000);

      const leagueFilter = getLeagueFilter(page);
      const options = leagueFilter.locator("option");
      const optionCount = await options.count();

      expect(optionCount).toBeGreaterThan(1);

      await leagueFilter.selectOption({ index: 1 });
      await waitForPageReady(page, 2000);

      expect(getUrlParam(page, "league_id")).toBeTruthy();

      await leagueFilter.selectOption("");
      await waitForPageReady(page, 2000);

      expect(getUrlParam(page, "league_id")).toBeNull();
      await verifyChartRenders(page);
    });

    test("should update chart when league filter changes", async ({ page }) => {
      await waitForPageReady(page, 3000);

      const leagueFilter = getLeagueFilter(page);
      const options = leagueFilter.locator("option");
      const optionCount = await options.count();

      expect(optionCount).toBeGreaterThan(2);

      await leagueFilter.selectOption({ index: 1 });
      await waitForPageReady(page, 2000);
      await verifyChartRenders(page);

      await leagueFilter.selectOption({ index: 2 });
      await waitForPageReady(page, 2000);
      await verifyChartRenders(page);
    });
  });

  test.describe("Error Handling", () => {
    test("should display error message when fetch fails", async ({ page }) => {
      await page.route("**/leaders/career-totals*", (route) => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: "Internal Server Error" }),
        });
      });

      await navigateAndWait(page, "/charts");
      await waitForPageReady(page, 3000);

      const hasError = await checkForChartError(page);
      expect(hasError).toBe(true);

      const errorMessage = page.getByText("Failed to load career totals data.");
      await expect(errorMessage).toBeVisible();
    });
  });

  test.describe("Compare Players", () => {
    function getPlayerIndex(playerLabel: string): number {
      return playerLabel === "Player 1" ? 0 : 1;
    }

    async function switchToCompareTab(page: Page) {
      const compareTab = page.getByRole("button", { name: "Compare Players" });
      await compareTab.click();
      await page.waitForURL(/.*view=compare.*/, { timeout: 5000 });
      await waitForPageReady(page, 2000);
      await page.getByRole("heading", { name: "Compare Players" }).waitFor({
        state: "visible",
        timeout: 15000,
      });
      await page
        .getByText("Player 1", { exact: true })
        .waitFor({ state: "visible", timeout: 15000 });
      await page
        .getByText("Player 2", { exact: true })
        .waitFor({ state: "visible", timeout: 15000 });
    }

    async function searchForPlayer(
      page: Page,
      playerLabel: string,
      query: string,
    ) {
      await page
        .getByText(playerLabel, { exact: true })
        .waitFor({ state: "visible", timeout: 15000 });

      const playerIndex = getPlayerIndex(playerLabel);
      const searchInput = page
        .getByPlaceholder("Search for a player...")
        .nth(playerIndex);

      await searchInput.waitFor({ state: "visible", timeout: 15000 });
      await searchInput.fill(query);
      await Promise.race([
        page.waitForSelector('[class*="bg-slate-700"] button', {
          state: "visible",
          timeout: 5000,
        }),
        page.waitForSelector("text=No players found", {
          state: "visible",
          timeout: 5000,
        }),
        page.waitForSelector("text=Searching...", {
          state: "visible",
          timeout: 5000,
        }),
      ]).catch(() => {});
    }

    async function waitForSearchResults(page: Page) {
      await page
        .waitForSelector("text=Searching...", {
          state: "hidden",
          timeout: 5000,
        })
        .catch(() => {});
      await Promise.race([
        page.waitForSelector('[class*="bg-slate-700"] button', {
          state: "visible",
          timeout: 3000,
        }),
        page.waitForSelector("text=No players found", {
          state: "visible",
          timeout: 3000,
        }),
      ]).catch(() => {});
    }

    async function selectFirstPlayerResult(page: Page, playerLabel: string) {
      const playerIndex = getPlayerIndex(playerLabel);

      const allDropdowns = page
        .locator('[class*="bg-slate-700"]')
        .filter({ hasText: /Player|No players found/ });
      const visibleCount = await allDropdowns.count();
      const targetDropdown =
        visibleCount === 1
          ? allDropdowns.first()
          : allDropdowns.nth(playerIndex);

      await expect(targetDropdown).toBeVisible({ timeout: 5000 });

      const resultButtons = targetDropdown.locator("button");
      await expect(resultButtons.first()).toBeVisible({ timeout: 5000 });

      const responsePromise = page
        .waitForResponse(
          (response) => {
            const url = response.url();
            return url.includes("/players/") && !url.includes("/goals");
          },
          { timeout: 20000 },
        )
        .catch(() => null);

      await resultButtons.first().click();
      await page.waitForTimeout(300);

      const response = await responsePromise;
      if (!response) {
        throw new Error(
          "Player details API call was not made or did not complete within 20 seconds.",
        );
      }

      await page.waitForTimeout(500);
    }

    async function waitForPlayerLoaded(page: Page, playerLabel: string) {
      const playerIndex = getPlayerIndex(playerLabel);

      const seasonSelector = page.getByRole("combobox").nth(playerIndex);
      const selectSeasonLabel = page
        .getByText("Select Season")
        .nth(playerIndex);
      const errorMessage = page.getByText(/Error:/i);

      await Promise.race([
        seasonSelector.waitFor({ state: "visible", timeout: 20000 }),
        selectSeasonLabel.waitFor({ state: "visible", timeout: 20000 }),
        errorMessage.waitFor({ state: "visible", timeout: 20000 }),
      ]);

      const hasSelector = await seasonSelector.isVisible().catch(() => false);
      const hasLabel = await selectSeasonLabel.isVisible().catch(() => false);
      const hasError = await errorMessage.isVisible().catch(() => false);

      if (hasError) {
        const errorText = await errorMessage.textContent();
        throw new Error(`Player details failed to load: ${errorText}`);
      }

      if (!hasSelector && !hasLabel) {
        throw new Error(
          `Player details loaded but season selector not visible for ${playerLabel}`,
        );
      }
    }

    async function selectPlayer(
      page: Page,
      playerLabel: string,
      searchQuery: string,
    ) {
      await searchForPlayer(page, playerLabel, searchQuery);
      await waitForSearchResults(page);
      await selectFirstPlayerResult(page, playerLabel);
      await waitForPlayerLoaded(page, playerLabel);
    }

    async function selectTwoPlayers(page: Page) {
      await selectPlayer(page, "Player 1", "test");
      await selectPlayer(page, "Player 2", "test");
    }

    test("should switch to Compare Players tab", async ({ page }) => {
      await waitForPageReady(page, 3000);

      const compareTab = page.getByRole("button", { name: "Compare Players" });
      await expect(compareTab).toBeVisible();

      await switchToCompareTab(page);

      const compareHeading = page.getByRole("heading", {
        name: "Compare Players",
      });
      await expect(compareHeading).toBeVisible();

      const url = page.url();
      expect(url).toContain("view=compare");
    });

    test.describe("Compare Players - Setup", () => {
      test.beforeEach(async ({ page }) => {
        await waitForPageReady(page, 3000);
        await switchToCompareTab(page);
      });

      test("should display player search inputs", async ({ page }) => {
        const player1Input = page
          .getByPlaceholder("Search for a player...")
          .first();
        const player2Input = page
          .getByPlaceholder("Search for a player...")
          .nth(1);

        await expect(player1Input).toBeVisible({ timeout: 15000 });
        await expect(player2Input).toBeVisible({ timeout: 15000 });
      });

      test("should show search results when typing in player search", async ({
        page,
      }) => {
        await searchForPlayer(page, "Player 1", "test");
        await waitForSearchResults(page);

        const resultsDropdown = page.locator('[class*="bg-slate-700"]').filter({
          hasText: /Player|No players found/,
        });
        await expect(resultsDropdown).toBeVisible({ timeout: 5000 });
      });

      test("should display loading state when searching", async ({ page }) => {
        await page.route("**/search*", async (route) => {
          await new Promise((resolve) => setTimeout(resolve, 2000));
          await route.continue();
        });

        const searchInput = page
          .getByPlaceholder("Search for a player...")
          .first();
        await searchInput.waitFor({ state: "visible", timeout: 15000 });
        await searchInput.fill("test");

        await expect(page.getByText("Searching...")).toBeVisible({
          timeout: 5000,
        });
        await expect(page.getByText("Searching...")).toBeHidden({
          timeout: 20000,
        });
      });

      test("should display empty state when no players selected", async ({
        page,
      }) => {
        const emptyState = page.getByText("Select two players to compare");
        await expect(emptyState).toBeVisible();
      });
    });

    test.describe("Compare Players - Player Selection", () => {
      test.beforeEach(async ({ page }) => {
        await waitForPageReady(page, 3000);
        await switchToCompareTab(page);
      });

      test("should select a player and display season selector", async ({
        page,
      }) => {
        await selectPlayer(page, "Player 1", "test");

        const seasonSelector = page.getByRole("combobox").first();
        await expect(seasonSelector).toBeVisible();
      });

      test("should display chart when both players are selected", async ({
        page,
      }) => {
        await selectTwoPlayers(page);

        const chartContainer = page.getByTestId("compare-players-radar-chart");
        await expect(chartContainer).toBeVisible({ timeout: 5000 });

        const radarChart = chartContainer.locator("svg").first();
        await expect(radarChart).toBeVisible({ timeout: 5000 });

        const svgElements = radarChart.locator("*");
        const elementCount = await svgElements.count();
        expect(elementCount).toBeGreaterThan(0);
      });

      test("should allow selecting different seasons for each player", async ({
        page,
      }) => {
        await selectPlayer(page, "Player 1", "test");

        const player1SeasonSelector = page.getByRole("combobox").first();
        await expect(player1SeasonSelector).toBeVisible();

        const options = player1SeasonSelector.locator("option");
        const optionCount = await options.count();

        expect(optionCount).toBeGreaterThan(0);

        if (optionCount > 1) {
          const initialValue = await player1SeasonSelector.inputValue();
          expect(initialValue).toBeTruthy();

          await player1SeasonSelector.selectOption({ index: 1 });

          const newValue = await player1SeasonSelector.inputValue();
          expect(newValue).toBeTruthy();
          if (initialValue !== "career" || newValue !== "career") {
            expect(newValue).not.toBe(initialValue);
          }
        }
      });

      test("should display career totals option in season selector", async ({
        page,
      }) => {
        await selectPlayer(page, "Player 1", "test");

        const player1SeasonSelector = page.getByRole("combobox").first();
        await expect(player1SeasonSelector).toBeVisible();

        const careerOption = player1SeasonSelector.getByRole("option", {
          name: "Career Totals",
        });
        await expect(careerOption).toHaveCount(1);

        const careerOptionText = await careerOption.textContent();
        expect(careerOptionText).toBe("Career Totals");

        const selectedValue = await player1SeasonSelector.inputValue();
        expect(selectedValue).toBe("career");
      });

      test("should display clear button when player is selected", async ({
        page,
      }) => {
        await selectPlayer(page, "Player 1", "test");

        const clearButton = page.getByRole("button", { name: "Clear" }).first();
        await expect(clearButton).toBeVisible();
      });

      test("should clear player selection when clear button is clicked", async ({
        page,
      }) => {
        await selectPlayer(page, "Player 1", "test");

        const clearButton = page.getByRole("button", { name: "Clear" }).first();
        await expect(clearButton).toBeVisible();

        await clearButton.click();

        const searchInput = page
          .getByPlaceholder("Search for a player...")
          .first();
        await expect(searchInput).toHaveValue("", { timeout: 2000 });
      });
    });

    test("should handle error when player details fetch fails", async ({
      page,
    }) => {
      await page.route("**/players/*", (route) => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: "Internal Server Error" }),
        });
      });

      await waitForPageReady(page, 3000);
      await switchToCompareTab(page);

      await searchForPlayer(page, "Player 1", "test");
      await waitForSearchResults(page);

      await selectFirstPlayerResult(page, "Player 1");

      const errorMessage = page.getByText(/Error:/i);
      await expect(errorMessage).toBeVisible({ timeout: 10000 });
    });

    test("should maintain tab state in URL", async ({ page }) => {
      await waitForPageReady(page, 3000);

      await switchToCompareTab(page);

      const url = page.url();
      expect(url).toContain("view=compare");

      await page.reload();
      await waitForPageReady(page, 3000);

      const compareHeading = page.getByRole("heading", {
        name: "Compare Players",
      });
      await expect(compareHeading).toBeVisible();
    });
  });
});
