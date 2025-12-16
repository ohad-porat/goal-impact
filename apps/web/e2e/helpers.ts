import { Page, expect } from '@playwright/test';

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
