import { test, expect, Page } from '@playwright/test';
import {
  getSeasonSelector,
  verifyTableWithData,
  hasNoGoals,
  navigateToPlayerViaSearch,
  navigateToGoalLog,
} from './helpers';

test.describe('Players', () => {
  test.describe('Detail Page', () => {
    let playerId: number | null = null;

    test.beforeEach(async ({ page }) => {
      playerId = await navigateToPlayerViaSearch(page);
    });

    test('should navigate to player detail page', async ({ page }) => {
      if (playerId) {
        await expect(page).toHaveURL(`/players/${playerId}`);
      }
    });

    test('should display player name', async ({ page }) => {
      if (playerId) {
        const heading = page.getByRole('heading', { level: 1 });
        await expect(heading).toBeVisible();
        
        const headingText = await heading.textContent();
        expect(headingText).toBeTruthy();
        expect(headingText?.trim().length).toBeGreaterThan(0);
      }
    });

    test('should display player nation if available', async ({ page }) => {
      if (playerId) {
        const countryText = page.getByText(/Country:/);
        const isVisible = await countryText.isVisible().catch(() => false);
        
        if (isVisible) {
          await expect(countryText).toBeVisible();
          const countrySection = page.locator('text=/Country:/').locator('..');
          const countryValue = await countrySection.textContent();
          expect(countryValue).toBeTruthy();
          expect(countryValue?.trim().length).toBeGreaterThan('Country:'.length);
        }
      }
    });

    test('should display "View Goal Log" button', async ({ page }) => {
      if (playerId) {
        const goalLogButton = page.getByRole('link', { name: 'View Goal Log' });
        await expect(goalLogButton).toBeVisible();
        
        const href = await goalLogButton.getAttribute('href');
        expect(href).toBe(`/players/${playerId}/goals`);
      }
    });

    test('should display seasons table with data', async ({ page }) => {
      if (playerId) {
        await verifyTableWithData(page);
      }
    });
  });

  test.describe('Goal Log Page', () => {
    let playerId: number | null = null;

    test.beforeEach(async ({ page }) => {
      playerId = await navigateToPlayerViaSearch(page);
      
      if (playerId) {
        await navigateToGoalLog(page);
      }
    });

    test('should navigate from detail to goal log', async ({ page }) => {
      if (playerId) {
        await expect(page).toHaveURL(new RegExp(`/players/${playerId}/goals(\\?season=\\d+)?$`));
      }
    });

    test('should display goal log heading', async ({ page }) => {
      if (playerId) {
        const heading = page.getByRole('heading', { level: 1 });
        await expect(heading).toBeVisible();
        
        const headingText = await heading.textContent();
        expect(headingText).toBeTruthy();
        expect(headingText).toContain('Goal Log');
      }
    });

    test('should display "Back to Player" button', async ({ page }) => {
      if (playerId) {
        const backButton = page.getByRole('link', { name: 'Back to Player' });
        await expect(backButton).toBeVisible();
        
        const href = await backButton.getAttribute('href');
        expect(href).toBe(`/players/${playerId}`);
      }
    });

    test('should navigate back to player when clicking "Back to Player"', async ({ page }) => {
      if (playerId) {
        const backButton = page.getByRole('link', { name: 'Back to Player' });
        await backButton.click();
        await page.waitForLoadState('networkidle');
        
        await expect(page).toHaveURL(`/players/${playerId}`);
      }
    });

    test('should display season selector when goals exist', async ({ page }) => {
      if (playerId) {
        if (!(await hasNoGoals(page))) {
          const seasonSelector = getSeasonSelector(page);
          await expect(seasonSelector).toBeVisible();
        }
      }
    });

    test('should display goal log table when goals exist', async ({ page }) => {
      if (playerId) {
        if (!(await hasNoGoals(page))) {
          await verifyTableWithData(page);
        }
      }
    });

    test('should handle empty state when no goals', async ({ page }) => {
      if (playerId) {
        if (await hasNoGoals(page)) {
          const noGoalsText = page.getByText('No goals found for this player');
          await expect(noGoalsText).toBeVisible();
        }
      }
    });

    test.describe('Season Selector', () => {
      test('should have seasons available', async ({ page }) => {
        if (playerId) {
          if (!(await hasNoGoals(page))) {
            const seasonSelector = getSeasonSelector(page);
            const options = seasonSelector.locator('option');
            const optionCount = await options.count();
            
            expect(optionCount).toBeGreaterThan(0);
          }
        }
      });

      test('should change season when selecting different option', async ({ page }) => {
        if (playerId) {
          if (!(await hasNoGoals(page))) {
            const seasonSelector = getSeasonSelector(page);
            const options = seasonSelector.locator('option');
            const optionCount = await options.count();
            
            if (optionCount > 1) {
              const lastOptionValue = await options.nth(optionCount - 1).getAttribute('value');
              
              if (lastOptionValue) {
                const initialUrl = page.url();
                await seasonSelector.selectOption(lastOptionValue);
                await page.waitForLoadState('networkidle');
                
                const newUrl = page.url();
                expect(newUrl).not.toBe(initialUrl);
                expect(newUrl).toContain(`season=${lastOptionValue}`);
              }
            }
          }
        }
      });

      test('should update goal log table when season changes', async ({ page }) => {
        if (playerId) {
          if (!(await hasNoGoals(page))) {
            const seasonSelector = getSeasonSelector(page);
            const options = seasonSelector.locator('option');
            const optionCount = await options.count();
            
            if (optionCount > 1) {
              const tableRows = page.locator('tbody tr');
              const initialRowCount = await tableRows.count();
              
              if (initialRowCount > 0) {
                const initialFirstRowText = await tableRows.first().textContent();
                
                await seasonSelector.selectOption({ index: optionCount - 1 });
                await page.waitForLoadState('networkidle');
                
                const newTableRows = page.locator('tbody tr');
                const newRowCount = await newTableRows.count();
                const newFirstRowText = await newTableRows.first().textContent();
                
                expect(newRowCount).toBeGreaterThan(0);
                if (initialRowCount === newRowCount) {
                  expect(newFirstRowText).not.toBe(initialFirstRowText);
                }
              }
            }
          }
        }
      });

      test('should include season parameter in URL', async ({ page }) => {
        if (playerId) {
          if (!(await hasNoGoals(page))) {
            const seasonSelector = getSeasonSelector(page);
            await expect(seasonSelector).toBeVisible();
            const options = seasonSelector.locator('option');
            const optionCount = await options.count();
            
            if (optionCount > 0) {
              const firstOptionValue = await options.first().getAttribute('value');
              
              if (firstOptionValue) {
                expect(page.url()).toContain(`season=${firstOptionValue}`);
              }
            }
          }
        }
      });
    });
  });

});
