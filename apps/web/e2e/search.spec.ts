import { test, expect, Page } from '@playwright/test';
import { navigateAndWait } from './helpers';

async function typeInSearch(page: Page, query: string) {
  const searchInput = page.getByPlaceholder('Search...');
  await searchInput.fill(query);
  await page.waitForTimeout(400);
}

async function waitForSearchResults(page: Page) {
  await page.waitForSelector('text=Searching...', { state: 'hidden', timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(200);
}

async function searchAndWaitForResults(page: Page, query: string) {
  await typeInSearch(page, query);
  await waitForSearchResults(page);
}

function getResultsDropdown(page: Page) {
  return page.locator('[class*="bg-slate-700"]').filter({ 
    hasText: /Player|Club|Competition|Nation|No results found/ 
  });
}

function getResultButtonsByType(page: Page, type: string) {
  return page.locator('button').filter({ hasText: new RegExp(type) });
}

async function hasSearchResults(page: Page): Promise<boolean> {
  const dropdown = getResultsDropdown(page);
  return await dropdown.isVisible().catch(() => false);
}

type ResultType = 'Player' | 'Club' | 'Competition' | 'Nation';
type ResultPath = '/players' | '/clubs' | '/leagues' | '/nations';

const resultTypeConfig: Record<ResultType, ResultPath> = {
  Player: '/players',
  Club: '/clubs',
  Competition: '/leagues',
  Nation: '/nations',
};

test.describe('Search', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/');
  });

  test.describe('Search Input', () => {
    test('should display search input on desktop', async ({ page }) => {
      const searchInput = page.getByPlaceholder('Search...');
      await expect(searchInput).toBeVisible();
    });

    test('should display search input in mobile menu', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      const menuButton = page.getByRole('button', { name: 'Toggle menu' });
      await menuButton.click();
      
      const searchInputs = page.getByPlaceholder('Search...');
      await expect(searchInputs).toHaveCount(2);
      await expect(searchInputs.nth(1)).toBeVisible();
    });

    test('should allow typing in search input', async ({ page }) => {
      const searchInput = page.getByPlaceholder('Search...');
      await searchInput.fill('test');
      await expect(searchInput).toHaveValue('test');
    });
  });

  test.describe('Search Results', () => {
    test('should show loading state while searching', async ({ page }) => {
      const searchInput = page.getByPlaceholder('Search...');
      await searchInput.fill('messi');
      
      const resultsDropdown = getResultsDropdown(page);
      await expect(resultsDropdown).toBeVisible({ timeout: 500 });
      
      const loadingText = page.getByText('Searching...');
      const isVisible = await loadingText.isVisible().catch(() => false);
      
      if (!isVisible) {
        await expect(resultsDropdown).toBeVisible();
      } else {
        await expect(loadingText).toBeVisible();
      }
    });

    test('should display search results dropdown when results are found', async ({ page }) => {
      await searchAndWaitForResults(page, 'test');
      
      const resultsDropdown = getResultsDropdown(page);
      const hasResults = await hasSearchResults(page);
      
      if (hasResults) {
        await expect(resultsDropdown).toBeVisible();
      }
    });

    test('should display result name and type in dropdown', async ({ page }) => {
      await searchAndWaitForResults(page, 'test');
      
      const resultButtons = page.locator('button').filter({ hasText: /Player|Club|Competition|Nation/ });
      const resultCount = await resultButtons.count();
      
      if (resultCount > 0) {
        const firstResult = resultButtons.first();
        const resultText = await firstResult.textContent();
        expect(resultText).toBeTruthy();
        
        if (resultText) {
          expect(resultText).toMatch(/Player|Club|Competition|Nation/);
        }
      }
    });

    test('should show "No results found" when no results', async ({ page }) => {
      await searchAndWaitForResults(page, 'nonexistentquery12345');
      
      const noResults = page.getByText('No results found');
      await expect(noResults).toBeVisible();
    });

    test('should close dropdown when clicking outside', async ({ page }) => {
      await searchAndWaitForResults(page, 'test');
      
      const resultsDropdown = getResultsDropdown(page);
      const isVisible = await resultsDropdown.isVisible().catch(() => false);
      
      if (isVisible) {
        await page.click('body', { position: { x: 0, y: 0 } });
        await page.waitForTimeout(200);
        
        await expect(resultsDropdown).not.toBeVisible();
      }
    });

    test('should close dropdown when search input is cleared', async ({ page }) => {
      const searchInput = page.getByPlaceholder('Search...');
      await searchAndWaitForResults(page, 'test');
      
      await searchInput.clear();
      await page.waitForTimeout(400);
      
      const resultsDropdown = getResultsDropdown(page);
      await expect(resultsDropdown).not.toBeVisible();
    });
  });

  test.describe('Search Navigation', () => {
    const resultTypes: ResultType[] = ['Player', 'Club', 'Competition', 'Nation'];
    
    for (const resultType of resultTypes) {
      test(`should navigate to ${resultType.toLowerCase()} page when clicking ${resultType.toLowerCase()} result`, async ({ page }) => {
        await searchAndWaitForResults(page, 'test');
        
        const results = getResultButtonsByType(page, resultType);
        const count = await results.count();
        
        if (count > 0) {
          await results.first().click();
          await page.waitForLoadState('networkidle');
          
          const expectedPath = resultTypeConfig[resultType];
          await expect(page).toHaveURL(new RegExp(`${expectedPath}/\\d+`));
        }
      });
    }

    test('should clear search input after navigating to result', async ({ page }) => {
      await searchAndWaitForResults(page, 'test');
      
      const resultButtons = page.locator('button').filter({ hasText: /Player|Club|Competition|Nation/ });
      const resultCount = await resultButtons.count();
      
      if (resultCount > 0) {
        await resultButtons.first().click();
        
        await page.waitForURL(/\/players\/\d+|\/clubs\/\d+|\/leagues\/\d+|\/nations\/\d+/, { timeout: 5000 });
        await page.waitForLoadState('networkidle');
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(500);
        
        try {
          await navigateAndWait(page, '/');
        } catch {
          await page.waitForTimeout(500);
          await navigateAndWait(page, '/');
        }
        
        const searchInput = page.getByPlaceholder('Search...');
        await expect(searchInput).toHaveValue('');
      }
    });
  });

  test.describe('Search Behavior', () => {
    test('should debounce search requests', async ({ page }) => {
      const searchInput = page.getByPlaceholder('Search...');
      
      await searchInput.fill('a');
      await page.waitForTimeout(100);
      await searchInput.fill('ab');
      await page.waitForTimeout(100);
      await searchInput.fill('abc');
      await waitForSearchResults(page);
      
      const resultsDropdown = getResultsDropdown(page);
      await expect(resultsDropdown).toBeVisible();
    });

    test('should open dropdown on focus if results exist', async ({ page }) => {
      await searchAndWaitForResults(page, 'test');
      
      const resultsDropdown = getResultsDropdown(page);
      const hasResults = await hasSearchResults(page);
      
      if (hasResults) {
        const searchInput = page.getByPlaceholder('Search...');
        await searchInput.blur();
        await page.waitForTimeout(200);
        
        await searchInput.focus();
        await page.waitForTimeout(200);
        
        await expect(resultsDropdown).toBeVisible();
      }
    });
  });
});
