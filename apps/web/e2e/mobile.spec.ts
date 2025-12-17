import { test, expect, Page } from '@playwright/test';
import {
  navigateAndWait,
  navigateToFirstDetailPage,
  getGoalCards,
  getLeagueButtons,
  getSeasonSelector,
  verifyDetailPageHeading,
  verifyTableHasHorizontalScroll,
} from './helpers';

const MOBILE_VIEWPORT = { width: 375, height: 667 };

test.describe('Mobile', () => {
  test.use({ viewport: MOBILE_VIEWPORT });

  test.describe('Home Page', () => {
    test('should display league filter as dropdown on mobile', async ({ page }) => {
      await navigateAndWait(page, '/');
      
      const leagueSelect = page.locator('select').filter({ hasText: /All Leagues/ });
      await expect(leagueSelect).toBeVisible();
      
      const leagueButtons = getLeagueButtons(page);
      const buttonCount = await leagueButtons.count();
      
      if (buttonCount > 0) {
        for (const button of await leagueButtons.all()) {
          await expect(button).not.toBeVisible();
        }
      }
    });

    test('should display goal cards on mobile', async ({ page }) => {
      await navigateAndWait(page, '/');
      await page.waitForLoadState('networkidle');
      
      const goalCards = getGoalCards(page);
      const count = await goalCards.count();
      
      if (count > 0) {
        await expect(goalCards.first()).toBeVisible();
      }
    });
  });

  test.describe('List Pages', () => {
    for (const { name, url } of [
      { name: 'nations', url: '/nations' },
      { name: 'leagues', url: '/leagues' },
    ]) {
      test(`should display ${name} table responsively`, async ({ page }) => {
        await verifyTableHasHorizontalScroll(page, url);
      });
    }

    test('should display clubs in grid layout on mobile', async ({ page }) => {
      await navigateAndWait(page, '/clubs');
      
      const clubsGrid = page.locator('[class*="grid"]');
      const gridCount = await clubsGrid.count();
      
      if (gridCount > 0) {
        const firstGrid = clubsGrid.first();
        const className = await firstGrid.getAttribute('class');
        expect(className).toContain('grid');
        
        const gridBox = await firstGrid.boundingBox();
        if (gridBox) {
          expect(gridBox.width).toBeLessThanOrEqual(MOBILE_VIEWPORT.width);
        }
      }
    });
  });

  test.describe('Detail Pages', () => {
    test('should display nation detail page responsively', async ({ page }) => {
      const nationId = await navigateToFirstDetailPage(
        page,
        '/nations',
        'No nations found',
        /\/nations\/(\d+)/
      );
      
      if (nationId) {
        await verifyDetailPageHeading(page);
      }
    });

    test('should display league detail page responsively', async ({ page }) => {
      const leagueId = await navigateToFirstDetailPage(
        page,
        '/leagues',
        'No leagues found',
        /\/leagues\/(\d+)/
      );
      
      if (leagueId) {
        await verifyDetailPageHeading(page);
        const seasonSelector = getSeasonSelector(page);
        await expect(seasonSelector).toBeVisible();
      }
    });

    test('should display club detail page responsively', async ({ page }) => {
      const clubId = await navigateToFirstDetailPage(
        page,
        '/clubs',
        'No clubs data available',
        /\/clubs\/(\d+)/
      );
      
      if (clubId) {
        await verifyDetailPageHeading(page);
        const table = page.locator('table');
        await expect(table).toBeVisible();
      }
    });

    test('should display player detail page responsively', async ({ page }) => {
      await navigateAndWait(page, '/');
      
      const menuButton = page.getByRole('button', { name: 'Toggle menu' });
      await menuButton.click();
      
      const searchInput = page.getByPlaceholder('Search...').nth(1);
      await searchInput.fill('test');
      await page.waitForSelector('text=Searching...', { state: 'hidden', timeout: 5000 }).catch(() => {});
      await page.waitForLoadState('networkidle');
      
      const playerResults = page.locator('button').filter({ hasText: /Player/ });
      const count = await playerResults.count();
      
      if (count > 0) {
        await playerResults.first().click();
        await page.waitForLoadState('networkidle');
        
        const url = page.url();
        const match = url.match(/\/players\/(\d+)/);
        if (match) {
          await verifyDetailPageHeading(page);
          
          const mainContent = page.locator('main');
          await expect(mainContent).toBeVisible();
        }
      }
    });
  });

  test.describe('Touch Interactions', () => {
    test.use({ hasTouch: true });
    
    test('should handle tap on table rows', async ({ page }) => {
      await navigateAndWait(page, '/nations');
      
      const rows = page.locator('tbody tr');
      const count = await rows.count();
      
      if (count > 0) {
        const firstRow = rows.first();
        const link = firstRow.getByRole('link');
        const linkCount = await link.count();
        
        if (linkCount > 0) {
          await link.first().tap();
          await page.waitForLoadState('networkidle');
          
          await expect(page).toHaveURL(/\/nations\/\d+/);
        }
      }
    });
  });

  test.describe('Responsive Layout', () => {
    test('should display content within viewport', async ({ page }) => {
      await navigateAndWait(page, '/');
      
      const mainContent = page.locator('main');
      await expect(mainContent).toBeVisible();
      
      const mainBox = await mainContent.boundingBox();
      if (mainBox) {
        expect(mainBox.width).toBeLessThanOrEqual(MOBILE_VIEWPORT.width);
      }
    });
  });
});
