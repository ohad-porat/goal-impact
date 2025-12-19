import { test, expect, Page } from '@playwright/test';
import {
  navigateAndWait,
  navigateToFirstDetailPage,
  navigateToGoalLog,
  verifyTableWithData,
  verifyEmptyStateOrContent,
} from './helpers';

async function navigateToSeasonRoster(
  page: Page
): Promise<number> {
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveURL(/\/clubs\/\d+$/);
  
  const seasonLinks = page.locator('a[href*="/seasons?season="]');
  await expect(seasonLinks.first()).toBeVisible({ timeout: 5000 });
  const count = await seasonLinks.count();
  expect(count).toBeGreaterThan(0);
  
  const firstLink = seasonLinks.first();
  const href = await firstLink.getAttribute('href');
  expect(href).toBeTruthy();
  
  const match = href!.match(/season=(\d+)/);
  expect(match).toBeTruthy();
  
  const seasonId = parseInt(match![1]);
  await firstLink.click();
  await page.waitForLoadState('networkidle');
  return seasonId;
}

function getClubLinks(page: Page) {
  return page.locator('a[href^="/clubs/"]');
}

test.describe('Clubs', () => {
  test.describe('List Page', () => {
    test.beforeEach(async ({ page }) => {
      await navigateAndWait(page, '/clubs');
    });

    test('should display clubs page heading', async ({ page }) => {
      await expect(page.getByRole('heading', { name: 'Top Clubs' })).toBeVisible();
    });

    test('should display clubs organized by nation', async ({ page }) => {
      const clubLinks = getClubLinks(page);
      await verifyEmptyStateOrContent(page, 'No clubs data available', clubLinks);
      
      const nationHeadings = page.locator('h2').filter({ hasText: /^[A-Za-z\s]+$/ });
      const nationCount = await nationHeadings.count();
      const linkCount = await clubLinks.count();
      
      expect(linkCount).toBeGreaterThan(0);
      expect(nationCount).toBeGreaterThan(0);
    });

    test('should display club links with valid hrefs', async ({ page }) => {
      const clubLinks = getClubLinks(page);
      const linkCount = await clubLinks.count();
      
      expect(linkCount).toBeGreaterThan(0);
      
      const firstLink = clubLinks.first();
      await expect(firstLink).toBeVisible();
      const href = await firstLink.getAttribute('href');
      expect(href).toMatch(/^\/clubs\/\d+$/);
    });
  });

  test.describe('Detail Page', () => {
    let clubId: number | null = null;

    test.beforeEach(async ({ page }) => {
      clubId = await navigateToFirstDetailPage(
        page,
        '/clubs',
        'No clubs data available',
        /\/clubs\/(\d+)/
      );
    });

    test('should navigate from list to detail page', async ({ page }) => {
      expect(clubId).not.toBeNull();
      await expect(page).toHaveURL(`/clubs/${clubId}`);
    });

    test('should display club name and nation', async ({ page }) => {
      expect(clubId).not.toBeNull();
      await expect(page).toHaveURL(`/clubs/${clubId}`);
      
      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
      
      const headingText = await heading.textContent();
      expect(headingText).toBeTruthy();
      expect(headingText?.trim().length).toBeGreaterThan(0);
      
      const nationText = page.locator('p').filter({ hasText: /England|Spain|Unknown Nation/ });
      await expect(nationText.first()).toBeVisible({ timeout: 5000 });
      const nationContent = await nationText.first().textContent();
      expect(nationContent).toBeTruthy();
      expect(nationContent!.trim().length).toBeGreaterThan(0);
    });

    test('should display seasons table with data', async ({ page }) => {
      expect(clubId).not.toBeNull();
      
      await verifyTableWithData(page);
      
      const seasonLinks = page.locator('a[href*="/seasons?season="]');
      const linkCount = await seasonLinks.count();
      expect(linkCount).toBeGreaterThan(0);
      
      const firstLink = seasonLinks.first();
      const href = await firstLink.getAttribute('href');
      expect(href).toMatch(/\/clubs\/\d+\/seasons\?season=\d+/);
    });
  });

  test.describe('Season Roster Page', () => {
    let clubId: number | null = null;
    let seasonId: number | null = null;

    test.beforeEach(async ({ page }) => {
      clubId = await navigateToFirstDetailPage(
        page,
        '/clubs',
        'No clubs data available',
        /\/clubs\/(\d+)/
      );
      
      expect(clubId).not.toBeNull();
      seasonId = await navigateToSeasonRoster(page);
      expect(seasonId).not.toBeNull();
    });

    test('should navigate from detail to season roster', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons?season=${seasonId}`);
    });

    test('should display season roster heading with club and season info', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      
      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
      
      const headingText = await heading.textContent();
      expect(headingText).toBeTruthy();
      expect(headingText?.trim().length).toBeGreaterThan(0);
    });

    test('should display "View Goal Log" button', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      
      const goalLogButton = page.getByRole('link', { name: 'View Goal Log' });
      await expect(goalLogButton).toBeVisible();
      
      const href = await goalLogButton.getAttribute('href');
      expect(href).toMatch(/\/clubs\/\d+\/seasons\/goals\?season=\d+/);
    });

    test('should display roster table with player data', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      await verifyTableWithData(page);
    });
  });

  test.describe('Goal Log Page', () => {
    let clubId: number | null = null;
    let seasonId: number | null = null;

    test.beforeEach(async ({ page }) => {
      clubId = await navigateToFirstDetailPage(
        page,
        '/clubs',
        'No clubs data available',
        /\/clubs\/(\d+)/
      );
      
      expect(clubId).not.toBeNull();
      seasonId = await navigateToSeasonRoster(page);
      expect(seasonId).not.toBeNull();
      await navigateToGoalLog(page);
    });

    test('should navigate from season roster to goal log', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons/goals?season=${seasonId}`);
    });

    test('should display goal log heading with club and season info', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons/goals?season=${seasonId}`);
      
      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
      
      const headingText = await heading.textContent();
      expect(headingText).toBeTruthy();
      expect(headingText).toContain('Goal Log');
    });

    test('should display "Back to Roster" button', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      
      const backButton = page.getByRole('link', { name: 'Back to Roster' });
      await expect(backButton).toBeVisible();
      
      const href = await backButton.getAttribute('href');
      expect(href).toMatch(/\/clubs\/\d+\/seasons\?season=\d+/);
    });

    test('should navigate back to roster when clicking "Back to Roster"', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      
      const backButton = page.getByRole('link', { name: 'Back to Roster' });
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons?season=${seasonId}`);
    });

    test('should display goal log table with data', async ({ page }) => {
      expect(clubId).not.toBeNull();
      expect(seasonId).not.toBeNull();
      await verifyTableWithData(page);
    });
  });

  test.describe('Navigation Flow', () => {
    test('should navigate through complete flow: list → detail → roster → goal log → back', async ({ page }) => {
      const clubId = await navigateToFirstDetailPage(
        page,
        '/clubs',
        'No clubs data available',
        /\/clubs\/(\d+)/
      );
      
      expect(clubId).not.toBeNull();
      
      const seasonId = await navigateToSeasonRoster(page);
      expect(seasonId).not.toBeNull();
      
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons?season=${seasonId}`);
      
      await navigateToGoalLog(page);
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons/goals?season=${seasonId}`);
      
      const backButton = page.getByRole('link', { name: 'Back to Roster' });
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveURL(`/clubs/${clubId}/seasons?season=${seasonId}`);
    });
  });
});
