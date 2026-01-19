import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLeaderFilters } from "./useLeaderFilters";

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
  useSearchParams: vi.fn(),
}));

describe("useLeaderFilters", () => {
  const mockPush = vi.fn();
  const mockRouter = {
    push: mockPush,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue(mockRouter);
  });

  describe("Reading URL parameters", () => {
    it("should parse valid league_id and season_id from URL params into numbers and preserve string values", () => {
      const mockSearchParams = new URLSearchParams("league_id=5&season_id=10");
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      expect(result.current.leagueId).toBe(5);
      expect(result.current.seasonId).toBe(10);
      expect(result.current.selectedLeagueId).toBe("5");
      expect(result.current.selectedSeasonId).toBe("10");
    });

    it("should return undefined for leagueId and seasonId when URL parameters are missing", () => {
      const mockSearchParams = new URLSearchParams();
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      expect(result.current.leagueId).toBeUndefined();
      expect(result.current.seasonId).toBeUndefined();
      expect(result.current.selectedLeagueId).toBeNull();
      expect(result.current.selectedSeasonId).toBeNull();
    });

    it("should return undefined for invalid numeric parameters but preserve original string values in selectedLeagueId and selectedSeasonId", () => {
      const mockSearchParams = new URLSearchParams(
        "league_id=abc&season_id=xyz",
      );
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      expect(result.current.leagueId).toBeUndefined();
      expect(result.current.seasonId).toBeUndefined();
      expect(result.current.selectedLeagueId).toBe("abc");
      expect(result.current.selectedSeasonId).toBe("xyz");
    });
  });

  describe("updateParams", () => {
    it("should update multiple parameters (league_id and season_id) and navigate with correct view parameter", () => {
      const mockSearchParams = new URLSearchParams("league_id=5");
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      result.current.updateParams("by-season", {
        season_id: "10",
        league_id: "7",
      });

      expect(mockPush).toHaveBeenCalledWith(
        "/leaders?league_id=7&view=by-season&season_id=10",
        {
          scroll: false,
        },
      );
    });

    it("should set view parameter to provided value when it is not present in URL", () => {
      const mockSearchParams = new URLSearchParams("league_id=5");
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      result.current.updateParams("career", {
        league_id: "7",
      });

      expect(mockPush).toHaveBeenCalledWith(
        "/leaders?league_id=7&view=career",
        {
          scroll: false,
        },
      );
    });

    it("should preserve existing view parameter when updating other parameters", () => {
      const mockSearchParams = new URLSearchParams(
        "view=by-season&league_id=5",
      );
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      result.current.updateParams("career", {
        league_id: "7",
      });

      expect(mockPush).toHaveBeenCalledWith(
        "/leaders?view=by-season&league_id=7",
        {
          scroll: false,
        },
      );
    });

    it("should delete league_id parameter when value is null while preserving other parameters", () => {
      const mockSearchParams = new URLSearchParams("league_id=5&season_id=10");
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      result.current.updateParams("by-season", {
        league_id: null,
        season_id: "10",
      });

      const callArgs = mockPush.mock.calls[0][0];
      const url = new URL(`http://localhost${callArgs}`);
      expect(url.searchParams.has("league_id")).toBe(false);
      expect(url.searchParams.get("season_id")).toBe("10");
    });

    it("should handle multiple parameter updates (league_id, season_id, and custom params) in a single call", () => {
      const mockSearchParams = new URLSearchParams();
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      result.current.updateParams("by-season", {
        league_id: "5",
        season_id: "10",
        other_param: "value",
      });

      expect(mockPush).toHaveBeenCalledWith(
        "/leaders?view=by-season&league_id=5&season_id=10&other_param=value",
        { scroll: false },
      );
    });

    it("should preserve existing URL parameters that are not included in the update", () => {
      const mockSearchParams = new URLSearchParams(
        "existing_param=value&league_id=5",
      );
      (useSearchParams as any).mockReturnValue(mockSearchParams);

      const { result } = renderHook(() => useLeaderFilters());

      result.current.updateParams("by-season", {
        season_id: "10",
      });

      const callArgs = mockPush.mock.calls[0][0];
      const url = new URL(`http://localhost${callArgs}`);
      expect(url.searchParams.get("existing_param")).toBe("value");
      expect(url.searchParams.get("league_id")).toBe("5");
      expect(url.searchParams.get("season_id")).toBe("10");
    });
  });
});
