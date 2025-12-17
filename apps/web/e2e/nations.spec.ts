import { test, expect, Page } from '@playwright/test';
import {
  navigateAndWait,
  getFilteredTableRows,
  verifyEmptyStateOrContent,
  verifyTableHeaders,
} from './helpers';

async function verifyClickableLinks(
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

function getNationRows(page: Page) {
  return getFilteredTableRows(page, 'No nations found');
}

async function getFirstNationLink(page: Page) {
  const rows = getNationRows(page);
  const count = await rows.count();
  if (count > 0) {
    return rows.first().getByRole('link').first();
  }
  return null;
}

test.describe('Nations', () => {
  test.describe('List Page', () => {
    test.beforeEach(async ({ page }) => {
      await navigateAndWait(page, '/nations');
    });

    test('should display nations page heading', async ({ page }) => {
      await expect(page.getByRole('heading', { name: 'Nations' })).toBeVisible();
    });

    test('should display nations table with headers', async ({ page }) => {
      await verifyTableHeaders(page, ['Nation', 'FIFA Code', 'Governing Body', 'Players']);
    });

    test('should display nations in table with clickable links', async ({ page }) => {
      const rows = getNationRows(page);
      const count = await rows.count();
      
      if (count > 0) {
        const firstRow = rows.first();
        const nationLink = firstRow.getByRole('link').first();
        await expect(nationLink).toBeVisible();
        
        const rowText = await firstRow.textContent();
        expect(rowText).toBeTruthy();
        
        const href = await nationLink.getAttribute('href');
        expect(href).toMatch(/^\/nations\/\d+$/);
      }
    });

    test('should handle empty state when no nations', async ({ page }) => {
      const rows = getNationRows(page);
      await verifyEmptyStateOrContent(page, 'No nations found', rows);
    });
  });

  test.describe('Detail Page', () => {
    let nationId: number | null = null;

    test.beforeEach(async ({ page }) => {
      await navigateAndWait(page, '/nations');
      
      const nationLink = await getFirstNationLink(page);
      if (nationLink) {
        const href = await nationLink.getAttribute('href');
        if (href) {
          const match = href.match(/\/nations\/(\d+)/);
          if (match) {
            nationId = parseInt(match[1]);
            await nationLink.click();
            await page.waitForLoadState('networkidle');
          }
        }
      }
    });

    test('should navigate from list to detail page', async ({ page }) => {
      if (nationId) {
        await expect(page).toHaveURL(`/nations/${nationId}`);
      }
    });

    test('should display nation name and details', async ({ page }) => {
      if (nationId) {
        const heading = page.getByRole('heading', { name: /^[A-Za-z\s]+$/ }).first();
        await expect(heading).toBeVisible();
        
        const fifaCodeText = page.getByText(/FIFA Code:/);
        await expect(fifaCodeText).toBeVisible();
        
        const governingBodyText = page.getByText(/Governing Body:/);
        await expect(governingBodyText).toBeVisible();
      }
    });

    test.describe('Competitions List', () => {
      test('should display competitions section', async ({ page }) => {
        if (nationId) {
          await expect(page.getByRole('heading', { name: 'Leagues' })).toBeVisible();
        }
      });

      test('should display competitions list or empty state with clickable links', async ({ page }) => {
        if (nationId) {
          const competitionRows = getFilteredTableRows(page, 'No leagues found.');
          
          await verifyEmptyStateOrContent(page, 'No leagues found.', competitionRows);
          await verifyClickableLinks(page, 'a[href^="/leagues/"]', /^\/leagues\/\d+$/);
        }
      });
    });

    test.describe('Clubs Table', () => {
      test('should display clubs section', async ({ page }) => {
        if (nationId) {
          await expect(page.getByRole('heading', { name: 'Top Clubs' })).toBeVisible();
        }
      });

      test('should display clubs table with headers', async ({ page }) => {
        if (nationId) {
          await verifyTableHeaders(page, ['Club', 'Avg Pos']);
        }
      });

      test('should display clubs or empty state with clickable links', async ({ page }) => {
        if (nationId) {
          const clubRows = getFilteredTableRows(page, 'No qualifying clubs found.');
          
          await verifyEmptyStateOrContent(page, 'No qualifying clubs found.', clubRows);
          await verifyClickableLinks(page, 'a[href^="/clubs/"]', /^\/clubs\/\d+$/);
        }
      });

      test('should display average position for clubs', async ({ page }) => {
        if (nationId) {
          const clubRows = getFilteredTableRows(page, 'No qualifying clubs found.');
          const count = await clubRows.count();
          
          if (count > 0) {
            const firstRow = clubRows.first();
            const rowText = await firstRow.textContent();
            expect(rowText).toBeTruthy();
            expect(rowText).toMatch(/\d+/);
          }
        }
      });
    });

    test.describe('Players Table', () => {
      test('should display players section', async ({ page }) => {
        if (nationId) {
          await expect(page.getByRole('heading', { name: 'Top Players' })).toBeVisible();
        }
      });

      test('should display players table with headers', async ({ page }) => {
        if (nationId) {
          await verifyTableHeaders(page, ['Player', 'Career GV']);
        }
      });

      test('should display players or empty state with clickable links', async ({ page }) => {
        if (nationId) {
          const playerRows = getFilteredTableRows(page, 'No players found.');
          
          await verifyEmptyStateOrContent(page, 'No players found.', playerRows);
          await verifyClickableLinks(page, 'a[href^="/players/"]', /^\/players\/\d+$/);
        }
      });

      test('should display career goal value for players', async ({ page }) => {
        if (nationId) {
          const playerRows = getFilteredTableRows(page, 'No players found.');
          const count = await playerRows.count();
          
          if (count > 0) {
            const firstRow = playerRows.first();
            const rowText = await firstRow.textContent();
            expect(rowText).toBeTruthy();
            expect(rowText).toMatch(/\d+\.?\d*/);
          }
        }
      });
    });
  });

  test.describe('Navigation Flow', () => {
    test('should navigate from list to detail and back', async ({ page }) => {
      await navigateAndWait(page, '/nations');
      
      const nationLink = await getFirstNationLink(page);
      if (nationLink) {
        const nationName = await nationLink.textContent();
        await nationLink.click();
        await page.waitForLoadState('networkidle');
        
        if (nationName) {
          const heading = page.getByRole('heading', { name: nationName.trim() });
          await expect(heading).toBeVisible();
        }
        
        await page.goBack();
        await page.waitForLoadState('networkidle');
        
        await expect(page).toHaveURL('/nations');
        await expect(page.getByRole('heading', { name: 'Nations' })).toBeVisible();
      }
    });

    test('should navigate from detail to linked pages', async ({ page }) => {
      await navigateAndWait(page, '/nations');
      
      const nationLink = await getFirstNationLink(page);
      if (nationLink) {
        await nationLink.click();
        await page.waitForLoadState('networkidle');
        
        const competitionLinks = page.locator('a[href^="/leagues/"]');
        const competitionCount = await competitionLinks.count();
        
        if (competitionCount > 0) {
          await competitionLinks.first().click();
          await page.waitForLoadState('networkidle');
          await expect(page).toHaveURL(/\/leagues\/\d+/);
        }
      }
    });
  });
});
