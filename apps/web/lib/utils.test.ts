import { describe, it, expect } from "vitest";
import { getShortLeagueName } from "./utils";

describe("getShortLeagueName", () => {
  describe("Mapped league names", () => {
    it('should return "Série A" for "Campeonato Brasileiro Série A"', () => {
      expect(getShortLeagueName("Campeonato Brasileiro Série A")).toBe(
        "Série A",
      );
    });

    it('should return "Bundesliga" for "Fußball-Bundesliga"', () => {
      expect(getShortLeagueName("Fußball-Bundesliga")).toBe("Bundesliga");
    });
  });

  describe("Unmapped league names", () => {
    it("should return original name for unmapped leagues", () => {
      expect(getShortLeagueName("Premier League")).toBe("Premier League");
      expect(getShortLeagueName("La Liga")).toBe("La Liga");
    });
  });

  describe("Edge cases", () => {
    it("should return empty string for empty input", () => {
      expect(getShortLeagueName("")).toBe("");
    });

    it("should return empty string for whitespace-only input", () => {
      expect(getShortLeagueName("   ")).toBe("");
    });

    it("should trim leading/trailing whitespace before lookup", () => {
      expect(getShortLeagueName("  Campeonato Brasileiro Série A  ")).toBe(
        "Série A",
      );
      expect(getShortLeagueName("  Premier League  ")).toBe("Premier League");
    });

    it("should not match when case differs (case-sensitive matching)", () => {
      expect(getShortLeagueName("campeonato brasileiro série a")).toBe(
        "campeonato brasileiro série a",
      );
    });

    it("should not match when input contains the league name but is longer", () => {
      expect(getShortLeagueName("Campeonato Brasileiro Série A Extra")).toBe(
        "Campeonato Brasileiro Série A Extra",
      );
    });

    it("should return empty string for null or undefined input", () => {
      expect(getShortLeagueName(null as any)).toBe("");
      expect(getShortLeagueName(undefined as any)).toBe("");
    });
  });
});
