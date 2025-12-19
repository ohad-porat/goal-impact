import { test, expect } from '@playwright/test';
import { navigateAndWait, verifyHomePageLoaded, getGoalCards, getLeagueButtons } from './helpers';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/');
  });

  test.describe('Recent Impact Goals', () => {
    test('should display league filter buttons on desktop', async ({ page }) => {
      const allLeaguesButton = page.getByRole('button', { name: 'All Leagues' });
      await expect(allLeaguesButton).toBeVisible();
      
      const leagueButtons = getLeagueButtons(page);
      const count = await leagueButtons.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should display league filter dropdown on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      const leagueSelect = page.locator('select').filter({ hasText: /All Leagues/ });
      await expect(leagueSelect).toBeVisible();
    });

    test('should filter goals by league when clicking league button', async ({ page }) => {
      await page.waitForLoadState('networkidle');
      
      const leagueButtons = getLeagueButtons(page);
      const buttonCount = await leagueButtons.count();
      
      expect(buttonCount).toBeGreaterThan(0);
      
      const initialGoalCards = getGoalCards(page);
      const initialGoalCount = await initialGoalCards.count();
      
      expect(initialGoalCount).toBeGreaterThan(0);
      
      const firstLeagueButton = leagueButtons.first();
      await firstLeagueButton.click();
      await page.waitForLoadState('networkidle');
      
      await expect(firstLeagueButton).toHaveClass(/bg-orange-400/);
      
      const filteredGoalCards = getGoalCards(page);
      const filteredGoalCount = await filteredGoalCards.count();
      
      expect(filteredGoalCount).toBeLessThanOrEqual(initialGoalCount);
    });

    test('should reset to all leagues when clicking All Leagues button', async ({ page }) => {
      await page.waitForLoadState('networkidle');
      
      const allLeaguesButton = page.getByRole('button', { name: 'All Leagues' });
      const leagueButtons = getLeagueButtons(page);
      const buttonCount = await leagueButtons.count();
      
      expect(buttonCount).toBeGreaterThan(0);
      
      const initialGoalCards = getGoalCards(page);
      const initialGoalCount = await initialGoalCards.count();
      
      expect(initialGoalCount).toBeGreaterThan(0);
      
      await leagueButtons.first().click();
      await page.waitForLoadState('networkidle');
      
      await allLeaguesButton.click();
      await page.waitForLoadState('networkidle');
      await expect(allLeaguesButton).toHaveClass(/bg-orange-400/);
      await page.waitForTimeout(500);
      
      const resetGoalCards = getGoalCards(page);
      const resetGoalCount = await resetGoalCards.count();
      expect(resetGoalCount).toBe(initialGoalCount);
    });

    test('should display goals when available', async ({ page }) => {
      await page.waitForLoadState('networkidle');
      
      const errorMessage = page.getByText('Failed to load recent goals.');
      const goalCards = getGoalCards(page);
      
      const hasError = await errorMessage.isVisible().catch(() => false);
      const goalCount = await goalCards.count();
      
      if (hasError) {
        throw new Error('Failed to load recent goals - test cannot verify goals are displayed');
      }
      
      expect(goalCount).toBeGreaterThan(0);
      await expect(goalCards.first()).toBeVisible();
    });

    test('should display goal information correctly', async ({ page }) => {
      await page.waitForLoadState('networkidle');
      
      const goalCards = getGoalCards(page);
      const goalCount = await goalCards.count();
      
      expect(goalCount).toBeGreaterThan(0);
      
      const firstGoal = goalCards.first();
      
      await expect(firstGoal).toContainText('vs');
      
      const goalText = await firstGoal.textContent();
      expect(goalText).toBeTruthy();
      expect(goalText).toMatch(/Minute \d+/);
      expect(goalText).toMatch(/\+?\d+\.\d{2}/);
    });
  });

  test.describe('How It Works Section', () => {
    test('should display Goal Value explanation', async ({ page }) => {
      await expect(page.getByText(/Goal Value measures how much a goal changes/i)).toBeVisible();
    });

    test('should display calculation factors list', async ({ page }) => {
      await expect(page.getByText(/When it was scored:/i)).toBeVisible();
      await expect(page.getByText(/The score difference:/i)).toBeVisible();
      await expect(page.getByText(/Match outcome:/i)).toBeVisible();
    });

    test('should display Goal Value example explanation', async ({ page }) => {
      await expect(page.getByText(/A Goal Value of \+0\.64 means/i)).toBeVisible();
    });
  });
});
