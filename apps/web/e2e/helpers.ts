import { Page, expect, Locator } from "@playwright/test";

export async function navigateAndWait(page: Page, url: string) {
  await page.goto(url);
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(100);
}

export async function verifyHomePageLoaded(page: Page) {
  await expect(
    page.getByRole("heading", {
      name: /Evaluate soccer's most valuable goals/i,
    }),
  ).toBeVisible();
  await expect(
    page.getByText("Goal Value measures the significance of every goal"),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Recent Impact Goals" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "How it works" }),
  ).toBeVisible();
}

export function getGoalCards(page: Page) {
  return page.locator('[class*="bg-gray-50"]').filter({ hasText: /vs/ });
}

export function getLeagueButtons(page: Page) {
  return page
    .locator("button")
    .filter({ hasText: /Premier League|Serie A|La Liga|Bundesliga/ });
}

export function getFilteredTableRows(page: Page, excludeText: string) {
  return page.locator("tbody tr").filter({ hasNotText: excludeText });
}

export async function verifyEmptyStateOrContent(
  page: Page,
  emptyStateText: string,
  rowLocator: Locator,
) {
  const emptyState = page.getByText(emptyStateText);
  const hasEmptyState = await emptyState.isVisible().catch(() => false);
  const rowCount = await rowLocator.count();

  expect(hasEmptyState || rowCount > 0).toBe(true);

  if (hasEmptyState) {
    await expect(emptyState).toBeVisible();
  } else {
    expect(rowCount).toBeGreaterThan(0);
  }
}

export async function verifyTableHeaders(page: Page, headers: string[]) {
  for (const header of headers) {
    await expect(
      page.getByRole("columnheader", { name: header }),
    ).toBeVisible();
  }
}

export function getSeasonSelector(page: Page) {
  return page.locator("select").filter({ hasText: /20\d{2}/ });
}

export async function navigateToFirstDetailPage(
  page: Page,
  listUrl: string,
  emptyStateText: string,
  linkPattern: RegExp,
): Promise<number | null> {
  await navigateAndWait(page, listUrl);

  let link: Locator;
  const tableRows = getFilteredTableRows(page, emptyStateText);
  const rowCount = await tableRows.count();

  if (rowCount > 0) {
    link = tableRows.first().getByRole("link").first();
  } else {
    const basePath = listUrl.replace(/^\//, "");
    const directLinks = page.locator(`a[href^="/${basePath}/"]`);
    const linkCount = await directLinks.count();
    expect(linkCount).toBeGreaterThan(0);
    link = directLinks.first();
  }

  const href = await link.getAttribute("href");
  expect(href).toBeTruthy();

  const match = href!.match(linkPattern);
  expect(match).toBeTruthy();

  const id = parseInt(match![1]);
  await link.click();
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(200);
  return id;
}

export async function navigateToGoalLog(page: Page): Promise<void> {
  const goalLogButton = page.getByRole("link", { name: "View Goal Log" });
  await goalLogButton.click();
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(200);
}

export async function verifyTableWithData(page: Page): Promise<void> {
  const table = page.locator("table");
  await expect(table).toBeVisible();

  const tableRows = page.locator("tbody tr");
  const count = await tableRows.count();

  expect(count).toBeGreaterThan(0);

  const firstRow = tableRows.first();
  const rowText = await firstRow.textContent();
  expect(rowText).toBeTruthy();
  expect(rowText?.trim().length).toBeGreaterThan(0);
}

export async function waitForPageReady(page: Page, timeout: number = 2000) {
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(timeout);
}

export async function selectFilterOptionIfAvailable(
  page: Page,
  filterLocator: Locator,
  optionIndex: number,
): Promise<boolean> {
  const options = filterLocator.locator("option");
  const optionCount = await options.count();

  expect(optionCount).toBeGreaterThan(optionIndex);

  await filterLocator.selectOption({ index: optionIndex });
  await waitForPageReady(page);
  return true;
}

export function getUrlParam(page: Page, paramName: string): string | null {
  return new URL(page.url()).searchParams.get(paramName);
}

export async function verifyErrorMessage(
  page: Page,
  errorPattern: RegExp | string,
): Promise<void> {
  const errorMessage =
    typeof errorPattern === "string"
      ? page.getByText(errorPattern, { exact: false })
      : page.getByText(errorPattern);
  await expect(errorMessage).toBeVisible();
}

export async function verifyDetailPageHeading(page: Page): Promise<void> {
  const heading = page.getByRole("heading", { level: 1 });
  await expect(heading).toBeVisible();
  const headingText = await heading.textContent();
  expect(headingText?.trim().length).toBeGreaterThan(0);
}

export async function verifyTableHasHorizontalScroll(
  page: Page,
  url: string,
): Promise<void> {
  await navigateAndWait(page, url);
  const table = page.locator("table");
  await expect(table).toBeVisible();
  const tableContainer = table.locator("..");
  const className = await tableContainer.getAttribute("class");
  expect(className).toContain("overflow-x-auto");
}

export async function checkForChartError(page: Page): Promise<boolean> {
  const errorMessage = page.getByText("Failed to load career totals data.");
  return await errorMessage.isVisible().catch(() => false);
}
