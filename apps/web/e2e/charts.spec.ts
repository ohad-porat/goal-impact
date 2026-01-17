import { test, expect, Page } from '@playwright/test';
import {
  navigateAndWait,
  waitForPageReady,
  selectFilterOptionIfAvailable,
  getUrlParam,
  checkForChartError,
} from './helpers';

function getLeagueFilter(page: Page) {
  return page.locator('select#league-filter');
}

async function verifyChartRenders(page: Page) {
  const chartTitle = page.getByRole('heading', { name: 'Career Totals Scatter Chart' });
  await expect(chartTitle).toBeVisible();
  
  const emptyState = page.getByText('No data available for the selected league.');
  const hasEmptyState = await emptyState.isVisible().catch(() => false);
  
  if (hasEmptyState) {
    await expect(emptyState).toBeVisible();
    return;
  }
  
  const chartContainer = page.getByTestId('career-totals-scatter-chart');
  await expect(chartContainer).toBeVisible({ timeout: 5000 });
  
  const scatterChart = chartContainer.locator('svg').first();
  await expect(scatterChart).toBeVisible({ timeout: 5000 });
  
  const axisLabels = page.locator('text').filter({ hasText: /Total Goals|Total Goal Value/ });
  const axisLabelCount = await axisLabels.count();
  if (axisLabelCount > 0) {
    await expect(axisLabels.first()).toBeVisible({ timeout: 2000 });
  }
}

test.describe('Charts', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/charts');
  });

  test.describe('Chart Rendering', () => {
    test('should render scatter chart when data loads', async ({ page }) => {
      await waitForPageReady(page, 3000);
      
      const hasError = await checkForChartError(page);
      if (hasError) {
        throw new Error('Failed to load chart data - test cannot verify chart is displayed');
      }
      
      await verifyChartRenders(page);
    });
  });

  test.describe('League Filtering', () => {
    test('should filter by league when selecting league', async ({ page }) => {
      await waitForPageReady(page, 3000);
      
      const leagueFilter = getLeagueFilter(page);
      const initialUrl = page.url();
      
      const options = leagueFilter.locator('option');
      const optionCount = await options.count();
      
      expect(optionCount).toBeGreaterThan(1);
      
      const selected = await selectFilterOptionIfAvailable(page, leagueFilter, 1);
      
      expect(selected).toBe(true);
      
      const newUrl = page.url();
      expect(newUrl).not.toBe(initialUrl);
      expect(getUrlParam(page, 'league_id')).toBeTruthy();
      
      await waitForPageReady(page, 2000);
      await verifyChartRenders(page);
    });

    test('should reset to all leagues when selecting "All Leagues"', async ({ page }) => {
      await waitForPageReady(page, 3000);
      
      const leagueFilter = getLeagueFilter(page);
      const options = leagueFilter.locator('option');
      const optionCount = await options.count();
      
      expect(optionCount).toBeGreaterThan(1);
      
      await leagueFilter.selectOption({ index: 1 });
      await waitForPageReady(page, 2000);
      
      expect(getUrlParam(page, 'league_id')).toBeTruthy();
      
      await leagueFilter.selectOption('');
      await waitForPageReady(page, 2000);
      
      expect(getUrlParam(page, 'league_id')).toBeNull();
      await verifyChartRenders(page);
    });

    test('should update chart when league filter changes', async ({ page }) => {
      await waitForPageReady(page, 3000);
      
      const leagueFilter = getLeagueFilter(page);
      const options = leagueFilter.locator('option');
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

  test.describe('Error Handling', () => {
    test('should display error message when fetch fails', async ({ page }) => {
      await page.route('**/leaders/career-totals*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      });

      await navigateAndWait(page, '/charts');
      await waitForPageReady(page, 3000);

      const hasError = await checkForChartError(page);
      expect(hasError).toBe(true);
      
      const errorMessage = page.getByText('Failed to load career totals data.');
      await expect(errorMessage).toBeVisible();
    });
  });
});
