import { test, expect, Page } from "@playwright/test";
import { navigateAndWait, verifyErrorMessage } from "./helpers";

async function verifyErrorDisplay(page: Page): Promise<void> {
  const errorText = page.getByText(/Error:/i);
  await expect(errorText).toBeVisible();

  const className = await errorText.getAttribute("class");
  expect(className).toContain("text-red-400");
}

const resourceTypes = [
  { type: "nation", path: "/nations" },
  { type: "league", path: "/leagues" },
  { type: "club", path: "/clubs" },
  { type: "player", path: "/players" },
];

test.describe("Error Handling", () => {
  test.describe("Invalid IDs", () => {
    for (const { type, path } of resourceTypes) {
      test(`should display error for invalid ${type} ID`, async ({ page }) => {
        await navigateAndWait(page, `${path}/invalid`);
        await verifyErrorMessage(
          page,
          new RegExp(`The ${type} ID "invalid" is not valid`, "i"),
        );
      });
    }

    for (const { type, path } of resourceTypes) {
      test(`should display error for various non-numeric ${type} ID formats`, async ({
        page,
      }) => {
        const invalidIds = ["abc", "test-123", "null", "undefined"];

        for (const invalidId of invalidIds) {
          await navigateAndWait(page, `${path}/${invalidId}`);
          await verifyErrorMessage(
            page,
            new RegExp(`The ${type} ID "${invalidId}" is not valid`, "i"),
          );
        }
      });
    }
  });

  test.describe("Non-existent Resources", () => {
    for (const { type, path } of resourceTypes) {
      test(`should display error for non-existent ${type}`, async ({
        page,
      }) => {
        await navigateAndWait(page, `${path}/999999`);
        await verifyErrorMessage(
          page,
          new RegExp(
            `The requested ${type} could not be found or does not exist`,
            "i",
          ),
        );
      });
    }
  });

  test.describe("Missing or Invalid Season Parameters", () => {
    const clubSeasonPaths = [
      { name: "club seasons", path: "/clubs/1/seasons" },
      { name: "club goal log", path: "/clubs/1/seasons/goals" },
    ];

    for (const { name, path } of clubSeasonPaths) {
      test(`should display error for missing season parameter in ${name}`, async ({
        page,
      }) => {
        await navigateAndWait(page, path);
        await verifyErrorMessage(page, /Season parameter is required/i);
      });

      test(`should display error for invalid season parameter in ${name}`, async ({
        page,
      }) => {
        await navigateAndWait(page, `${path}?season=invalid`);
        await verifyErrorMessage(page, /Season parameter is required/i);
      });
    }
  });

  test.describe("Invalid Season Selection", () => {
    test("should display error for invalid season in league page", async ({
      page,
    }) => {
      await navigateAndWait(page, "/leagues/1?season=999999");
      await verifyErrorMessage(page, /The requested season is not valid/i);
    });

    test("should display error for invalid season in player goal log", async ({
      page,
    }) => {
      await navigateAndWait(page, "/players/1/goals?season=999999");
      await verifyErrorMessage(page, /No valid season found/i);
    });
  });

  test.describe("Error Display Component", () => {
    test("should display error messages with correct styling", async ({
      page,
    }) => {
      await navigateAndWait(page, "/nations/invalid");
      await verifyErrorDisplay(page);
    });
  });

  test.describe("Error Recovery", () => {
    test("should allow navigation away from error page", async ({ page }) => {
      await navigateAndWait(page, "/nations/invalid");
      await expect(page.getByText(/Error:/i)).toBeVisible();

      await page.getByRole("link", { name: "GOAL IMPACT" }).click();
      await page.waitForLoadState("networkidle");

      await expect(page).toHaveURL("/");
      await expect(
        page.getByRole("heading", {
          name: /Evaluate soccer's most valuable goals/i,
        }),
      ).toBeVisible();
    });

    test("should allow navigation to valid page from error", async ({
      page,
    }) => {
      await navigateAndWait(page, "/nations/invalid");
      await expect(page.getByText(/Error:/i)).toBeVisible();

      await page.getByRole("link", { name: "Nations" }).click();
      await page.waitForLoadState("networkidle");

      await expect(page).toHaveURL("/nations");
      await expect(
        page.getByRole("heading", { name: "Nations" }),
      ).toBeVisible();
    });
  });
});
