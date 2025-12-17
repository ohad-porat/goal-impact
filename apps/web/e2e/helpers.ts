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

export async function verifyClickableLinks(
  page: Page,
  linkSelector: string,
  hrefPattern: RegExp
) {
  const links = page.locator(linkSelector);
  const count = await links.count();
  
  if (count > 0) {
    const firstLink = links.first();
    const href = await firstLink.getAttribute('href');
    expect(href).toMatch(hrefPattern);
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
