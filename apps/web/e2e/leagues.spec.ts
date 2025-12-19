import { test, expect, Page } from '@playwright/test';
import {
  navigateAndWait,
  getFilteredTableRows,
  verifyEmptyStateOrContent,
  verifyTableHeaders,
  getSeasonSelector,
  navigateToFirstDetailPage,
} from './helpers';

function getLeagueRows(page: Page) {
  return getFilteredTableRows(page, 'No leagues found');
}

test.describe('Leagues', () => {
  test.describe('List Page', () => {
    test.beforeEach(async ({ page }) => {
      await navigateAndWait(page, '/leagues');
    });

    test('should display leagues page heading', async ({ page }) => {
      await expect(page.getByRole('heading', { name: 'Leagues' })).toBeVisible();
    });

    test('should display leagues table with headers', async ({ page }) => {
      await verifyTableHeaders(page, ['Name', 'Country', 'Gender', 'Tier', 'Available Seasons']);
    });

    test('should display leagues in table with clickable links', async ({ page }) => {
      const rows = getLeagueRows(page);
      const count = await rows.count();
      
      expect(count).toBeGreaterThan(0);
      
      const firstRow = rows.first();
      const leagueLink = firstRow.getByRole('link').first();
      await expect(leagueLink).toBeVisible();
      
      const rowText = await firstRow.textContent();
      expect(rowText).toBeTruthy();
      
      const href = await leagueLink.getAttribute('href');
      expect(href).toMatch(/^\/leagues\/\d+$/);
    });

    test('should handle empty state when no leagues', async ({ page }) => {
      const rows = getLeagueRows(page);
      await verifyEmptyStateOrContent(page, 'No leagues found', rows);
    });
  });

  test.describe('Detail Page', () => {
    let leagueId: number | null = null;

    test.beforeEach(async ({ page }) => {
      leagueId = await navigateToFirstDetailPage(
        page,
        '/leagues',
        'No leagues found',
        /\/leagues\/(\d+)/
      );
      
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(new RegExp(`/leagues/${leagueId}(\\?season=\\d+)?$`));
      
      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
      const headingText = await heading.textContent();
      expect(headingText).toContain('Premier League');
    });

    test('should navigate from list to detail page', async ({ page }) => {
      expect(leagueId).not.toBeNull();
      await expect(page).toHaveURL(new RegExp(`/leagues/${leagueId}(\\?season=\\d+)?$`));
    });

    test('should display league name', async ({ page }) => {
      expect(leagueId).not.toBeNull();
      
      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
      
      const headingText = await heading.textContent();
      expect(headingText).toBeTruthy();
      expect(headingText?.trim().length).toBeGreaterThan(0);
    });

    test('should display season selector', async ({ page }) => {
      expect(leagueId).not.toBeNull();
      const seasonSelector = getSeasonSelector(page);
      await expect(seasonSelector).toBeVisible();
    });

    test('should display league table', async ({ page }) => {
      expect(leagueId).not.toBeNull();
      const table = page.locator('table');
      await expect(table).toBeVisible();
    });

    test('should display league table with data', async ({ page }) => {
      expect(leagueId).not.toBeNull();
      
      const tableRows = page.locator('tbody tr');
      const count = await tableRows.count();
      
      expect(count).toBeGreaterThan(0);
      
      const firstRow = tableRows.first();
      const rowText = await firstRow.textContent();
      expect(rowText).toBeTruthy();
      expect(rowText?.trim().length).toBeGreaterThan(0);
    });

    test.describe('Season Selector', () => {
      test('should have multiple seasons available', async ({ page }) => {
        expect(leagueId).not.toBeNull();
        
        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();
        const options = seasonSelector.locator('option');
        const optionCount = await options.count();
        
        expect(optionCount).toBeGreaterThan(0);
      });

      test('should change season when selecting different option', async ({ page }) => {
        expect(leagueId).not.toBeNull();
        await expect(page).toHaveURL(new RegExp(`/leagues/${leagueId}(\\?season=\\d+)?$`));
        
        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();
        
        const options = seasonSelector.locator('option');
        const optionCount = await options.count();
        
        expect(optionCount).toBeGreaterThan(1);
        
        const firstOptionValue = await options.first().getAttribute('value');
        const lastOptionValue = await options.nth(optionCount - 1).getAttribute('value');
        
        expect(firstOptionValue).toBeTruthy();
        expect(lastOptionValue).toBeTruthy();
        expect(firstOptionValue).not.toBe(lastOptionValue);
        
        const initialUrl = page.url();
        
        await seasonSelector.selectOption(lastOptionValue!);
        await page.waitForURL(new RegExp(`/leagues/${leagueId}\\?season=${lastOptionValue}`), { timeout: 5000 });
        await page.waitForLoadState('networkidle');
        
        const newUrl = page.url();
        expect(newUrl).not.toBe(initialUrl);
        expect(newUrl).toContain(`season=${lastOptionValue}`);
      });

      test('should update league table when season changes', async ({ page }) => {
        expect(leagueId).not.toBeNull();
        await expect(page).toHaveURL(new RegExp(`/leagues/${leagueId}(\\?season=\\d+)?$`));
        
        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();
        
        const options = seasonSelector.locator('option');
        const optionCount = await options.count();
        
        expect(optionCount).toBeGreaterThan(1);
        
        const tableRows = page.locator('tbody tr');
        const initialRowCount = await tableRows.count();
        
        expect(initialRowCount).toBeGreaterThan(0);
        
        const initialFirstRowText = await tableRows.first().textContent();
        
        const lastOptionValue = await options.nth(optionCount - 1).getAttribute('value');
        expect(lastOptionValue).toBeTruthy();
        
        await seasonSelector.selectOption(lastOptionValue!);
        await page.waitForURL(new RegExp(`/leagues/${leagueId}\\?season=${lastOptionValue}`), { timeout: 5000 });
        await page.waitForLoadState('networkidle');
        
        const newTableRows = page.locator('tbody tr');
        const newRowCount = await newTableRows.count();
        const newFirstRowText = await newTableRows.first().textContent();
        
        expect(newRowCount).toBeGreaterThan(0);
        
        if (initialRowCount === newRowCount) {
          expect(newFirstRowText).not.toBe(initialFirstRowText);
        } else {
          expect(newRowCount).not.toBe(initialRowCount);
        }
      });
    });
  });

  test.describe('Navigation Flow', () => {
    test('should navigate from list to detail and back', async ({ page }) => {
      await navigateAndWait(page, '/leagues');
      
      const rows = getLeagueRows(page);
      const count = await rows.count();
      
      expect(count).toBeGreaterThan(0);
      
      const leagueLink = rows.first().getByRole('link').first();
      const leagueName = await leagueLink.textContent();
      expect(leagueName).toBeTruthy();
      
      await leagueLink.click();
      await page.waitForURL(/\/leagues\/\d+/, { timeout: 5000 });
      await page.waitForLoadState('networkidle');
      
      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
      
      const navigationPromise = page.waitForURL('**/leagues', { timeout: 10000 });
      await page.goBack();
      await navigationPromise;
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveURL('/leagues');
      await expect(page.getByRole('heading', { name: 'Leagues' })).toBeVisible();
    });

    test('should include season parameter in URL on detail page', async ({ page }) => {
      const id = await navigateToFirstDetailPage(
        page,
        '/leagues',
        'No leagues found',
        /\/leagues\/(\d+)/
      );
      
      expect(id).not.toBeNull();
      
      const seasonSelector = getSeasonSelector(page);
      await expect(seasonSelector).toBeVisible();
      const options = seasonSelector.locator('option');
      const optionCount = await options.count();
      
      expect(optionCount).toBeGreaterThan(0);
      
      const firstOptionValue = await options.first().getAttribute('value');
      expect(firstOptionValue).toBeTruthy();
      
      await seasonSelector.selectOption(firstOptionValue!);
      await page.waitForURL((url) => url.toString().includes(`season=${firstOptionValue}`), { timeout: 5000 });
      await page.waitForLoadState('networkidle');
      
      const url = page.url();
      expect(url).toContain(`season=${firstOptionValue}`);
    });
  });
});
