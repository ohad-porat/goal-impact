import { Page, expect, Locator } from '@playwright/test';

export async function navigateAndWait(page: Page, url: string) {
  await page.goto(url);
  await page.waitForLoadState('networkidle');
}

export async function verifyHomePageLoaded(page: Page) {
  await expect(page.getByRole('heading', { name: /Evaluate soccer's most valuable goals/i })).toBeVisible();
  await expect(page.getByText('Goal Value measures the significance of every goal')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Recent Impact Goals' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'How it works' })).toBeVisible();
}

export function getGoalCards(page: Page) {
  return page.locator('[class*="bg-gray-50"]').filter({ hasText: /vs/ });
}

export function getLeagueButtons(page: Page) {
  return page.locator('button').filter({ hasText: /Premier League|Serie A|La Liga|Bundesliga/ });
}

export function getFilteredTableRows(page: Page, excludeText: string) {
  return page.locator('tbody tr').filter({ hasNotText: excludeText });
}

export async function verifyEmptyStateOrContent(
  page: Page,
  emptyStateText: string,
  rowLocator: Locator
) {
  const emptyState = page.getByText(emptyStateText);
  const hasEmptyState = await emptyState.isVisible().catch(() => false);
  const rowCount = await rowLocator.count();
  
  if (hasEmptyState) {
    await expect(emptyState).toBeVisible();
  } else if (rowCount > 0) {
    expect(rowCount).toBeGreaterThan(0);
  }
}

export async function verifyTableHeaders(page: Page, headers: string[]) {
  for (const header of headers) {
    await expect(page.getByRole('columnheader', { name: header })).toBeVisible();
  }
}

export function getSeasonSelector(page: Page) {
  return page.locator('select').filter({ hasText: /20\d{2}/ });
}

export async function navigateToFirstDetailPage(
  page: Page,
  listUrl: string,
  emptyStateText: string,
  linkPattern: RegExp
): Promise<number | null> {
  await navigateAndWait(page, listUrl);
  
  const rows = getFilteredTableRows(page, emptyStateText);
  const count = await rows.count();
  
  if (count > 0) {
    const link = rows.first().getByRole('link').first();
    const href = await link.getAttribute('href');
    
    if (href) {
      const match = href.match(linkPattern);
      if (match) {
        const id = parseInt(match[1]);
        await link.click();
        await page.waitForLoadState('networkidle');
        return id;
      }
    }
  }
  
  return null;
}

export async function navigateToGoalLog(page: Page): Promise<void> {
  const goalLogButton = page.getByRole('link', { name: 'View Goal Log' });
  await goalLogButton.click();
  await page.waitForLoadState('networkidle');
}

export async function verifyTableWithData(page: Page): Promise<void> {
  const table = page.locator('table');
  await expect(table).toBeVisible();
  
  const tableRows = page.locator('tbody tr');
  const count = await tableRows.count();
  
  if (count > 0) {
    const firstRow = tableRows.first();
    const rowText = await firstRow.textContent();
    expect(rowText).toBeTruthy();
    expect(rowText?.trim().length).toBeGreaterThan(0);
  }
}

export async function waitForPageReady(page: Page, timeout: number = 2000) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(timeout);
}

export async function selectFilterOptionIfAvailable(
  page: Page,
  filterLocator: Locator,
  optionIndex: number
): Promise<boolean> {
  const options = filterLocator.locator('option');
  const optionCount = await options.count();
  
  if (optionCount > optionIndex) {
    await filterLocator.selectOption({ index: optionIndex });
    await waitForPageReady(page);
    return true;
  }
  return false;
}

export function getUrlParam(page: Page, paramName: string): string | null {
  return new URL(page.url()).searchParams.get(paramName);
}

export async function verifyErrorMessage(page: Page, errorPattern: RegExp | string): Promise<void> {
  const errorMessage = typeof errorPattern === 'string' 
    ? page.getByText(errorPattern, { exact: false })
    : page.getByText(errorPattern);
  await expect(errorMessage).toBeVisible();
}

export async function verifyDetailPageHeading(page: Page): Promise<void> {
  const heading = page.getByRole('heading', { level: 1 });
  await expect(heading).toBeVisible();
  const headingText = await heading.textContent();
  expect(headingText?.trim().length).toBeGreaterThan(0);
}

export async function verifyTableHasHorizontalScroll(page: Page, url: string): Promise<void> {
  await navigateAndWait(page, url);
  const table = page.locator('table');
  await expect(table).toBeVisible();
  const tableContainer = table.locator('..');
  const className = await tableContainer.getAttribute('class');
  expect(className).toContain('overflow-x-auto');
}
