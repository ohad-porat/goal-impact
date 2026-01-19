import { test, expect, Page } from "@playwright/test";
import { navigateAndWait, verifyHomePageLoaded } from "./helpers";

const NAV_PAGES = [
  { link: "Nations", url: "/nations", heading: "Nations" },
  { link: "Leagues", url: "/leagues", heading: "Leagues" },
  { link: "Clubs", url: "/clubs", heading: "Top Clubs" },
  { link: "Leaders", url: "/leaders", heading: "Leaders" },
  { link: "Charts", url: "/charts", heading: "Charts" },
] as const;

const NAV_LINK_NAMES = [
  "Nations",
  "Leagues",
  "Clubs",
  "Leaders",
  "Charts",
] as const;

async function navigateToPage(
  page: Page,
  linkName: string,
  expectedUrl: string,
  expectedHeading: string,
) {
  await page.getByRole("link", { name: linkName }).click();
  await expect(page).toHaveURL(expectedUrl);
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(200);
  if (expectedHeading === "Leaders") {
    await expect(page.getByTestId("leaders-page-heading")).toBeVisible();
  } else {
    await expect(
      page.getByRole("heading", { name: expectedHeading }),
    ).toBeVisible();
  }
}

async function verifyHomePage(page: Page) {
  await expect(page).toHaveURL("/");
  await verifyHomePageLoaded(page);
}

async function verifyNavLinksVisible(page: Page, visible: boolean) {
  for (const linkName of NAV_LINK_NAMES) {
    await expect(page.getByRole("link", { name: linkName })).toBeVisible({
      visible,
    });
  }
}

function getMobileMenuButton(page: Page) {
  return page.getByRole("button", { name: "Toggle menu" });
}

async function openMobileMenu(page: Page) {
  const menuButton = getMobileMenuButton(page);
  await menuButton.click();
}

test.describe("Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, "/");
  });

  test.describe("Desktop Navigation", () => {
    test("should display all navigation links in desktop view", async ({
      page,
    }) => {
      await expect(
        page.getByRole("link", { name: "GOAL IMPACT" }),
      ).toBeVisible();
      await verifyNavLinksVisible(page, true);
      await expect(page.getByPlaceholder("Search...")).toBeVisible();
    });

    test("should navigate to home page when clicking logo", async ({
      page,
    }) => {
      await page.getByRole("link", { name: "GOAL IMPACT" }).click();
      await verifyHomePage(page);
    });

    for (const { link, url, heading } of NAV_PAGES) {
      test(`should navigate to ${link} page`, async ({ page }) => {
        await navigateToPage(page, link, url, heading);
      });
    }

    test("should maintain navbar visibility after navigation", async ({
      page,
    }) => {
      for (const { link } of NAV_PAGES) {
        await page.getByRole("link", { name: link }).click();
        await page.waitForLoadState("domcontentloaded");
        await page.waitForTimeout(200);
        await expect(
          page.getByRole("link", { name: "GOAL IMPACT" }),
        ).toBeVisible();
      }
    });
  });

  test.describe("Mobile Navigation", () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test("should show mobile menu button on mobile view", async ({ page }) => {
      await expect(getMobileMenuButton(page)).toBeVisible();
      await verifyNavLinksVisible(page, false);
    });

    test("should toggle mobile menu when clicking menu button", async ({
      page,
    }) => {
      const menuButton = getMobileMenuButton(page);

      await verifyNavLinksVisible(page, false);

      await menuButton.click();
      await verifyNavLinksVisible(page, true);

      await menuButton.click();
      await verifyNavLinksVisible(page, false);
    });

    test("should show search bar in mobile menu when opened", async ({
      page,
    }) => {
      await openMobileMenu(page);
      const searchInputs = page.getByPlaceholder("Search...");
      await expect(searchInputs).toHaveCount(2);
      await expect(searchInputs.nth(1)).toBeVisible();
    });

    test("should close mobile menu when clicking a link", async ({ page }) => {
      for (const { link, url } of NAV_PAGES) {
        await navigateAndWait(page, "/");
        await openMobileMenu(page);
        await expect(page.getByRole("link", { name: link })).toBeVisible();

        await page.getByRole("link", { name: link }).click();

        await expect(page).toHaveURL(url);
        await page.waitForLoadState("domcontentloaded");
        await page.waitForTimeout(200);
        await verifyNavLinksVisible(page, false);
      }
    });

    test("should navigate to all pages from mobile menu", async ({ page }) => {
      for (const { link, url, heading } of NAV_PAGES) {
        await navigateAndWait(page, "/");
        await openMobileMenu(page);
        await navigateToPage(page, link, url, heading);
      }
    });
  });

  test.describe("Logo Navigation", () => {
    test("should navigate to home from any page when clicking logo", async ({
      page,
    }) => {
      for (const { url } of NAV_PAGES) {
        await navigateAndWait(page, url);
        await page.getByRole("link", { name: "GOAL IMPACT" }).click();
        await verifyHomePage(page);
      }
    });
  });
});
