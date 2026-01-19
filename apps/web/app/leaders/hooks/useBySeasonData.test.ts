import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useBySeasonData } from "./useBySeasonData";
import { api } from "../../../lib/api";

vi.mock("../../../lib/api", () => ({
  api: {
    leadersBySeason: vi.fn((seasonId: number, leagueId?: number) => {
      const url = new URL("https://api.example.com/leaders/by-season");
      url.searchParams.set("season_id", seasonId.toString());
      if (leagueId !== undefined) {
        url.searchParams.set("league_id", leagueId.toString());
      }
      return url.toString();
    }),
  } as any,
}));

describe("useBySeasonData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("should not fetch when seasonId is undefined and return null data with no loading or error state", () => {
    const { result } = renderHook(() => useBySeasonData(undefined));

    expect(result.current.data).toBe(null);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("should fetch data when seasonId is provided without leagueId and update loading state correctly", async () => {
    const mockData = {
      top_goal_value: [
        {
          player_id: 1,
          player_name: "Player 1",
          clubs: "Club A",
          total_goal_value: 10.5,
          total_goals: 5,
          total_matches: 10,
        },
      ],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useBySeasonData(10));

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
    expect(global.fetch).toHaveBeenCalledWith(
      api.leadersBySeason(10, undefined),
      {
        cache: "no-cache",
      },
    );
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("should fetch data with both seasonId and leagueId", async () => {
    const mockData = {
      top_goal_value: [
        {
          player_id: 2,
          player_name: "Player 2",
          clubs: "Club B",
          total_goal_value: 8.3,
          total_goals: 4,
          total_matches: 8,
        },
      ],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useBySeasonData(10, 5));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(api.leadersBySeason(10, 5), {
      cache: "no-cache",
    });
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("should reset data to null when seasonId changes from a valid value to undefined", async () => {
    const mockData = {
      top_goal_value: [],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const { result, rerender } = renderHook(
      ({ seasonId }: { seasonId?: number }) => useBySeasonData(seasonId),
      {
        initialProps: { seasonId: 10 as number | undefined },
      },
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);

    rerender({ seasonId: undefined as number | undefined });

    expect(result.current.data).toBe(null);
    expect(result.current.loading).toBe(false);
  });

  it("should refetch when seasonId changes from 10 to 20 and reset data during loading", async () => {
    const mockData1 = { top_goal_value: [] };
    const mockData2 = { top_goal_value: [] };

    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockData1,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockData2,
      });

    const { result, rerender } = renderHook(
      ({ seasonId }: { seasonId: number }) => useBySeasonData(seasonId),
      {
        initialProps: { seasonId: 10 },
      },
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData1);

    rerender({ seasonId: 20 });

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData2);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it("should refetch when leagueId changes from 5 to 7 while seasonId remains the same", async () => {
    const mockData1 = { top_goal_value: [] };
    const mockData2 = { top_goal_value: [] };

    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockData1,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockData2,
      });

    const { result, rerender } = renderHook(
      ({ seasonId, leagueId }: { seasonId: number; leagueId?: number }) =>
        useBySeasonData(seasonId, leagueId),
      {
        initialProps: { seasonId: 10, leagueId: 5 },
      },
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    rerender({ seasonId: 10, leagueId: 7 });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it("should handle network fetch error by setting error state and logging to console", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});
    (global.fetch as any).mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useBySeasonData(10));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe("Failed to load by-season data.");
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "Error fetching by-season data:",
      expect.objectContaining({
        message: "Network error",
      }),
    );
    expect(global.fetch).toHaveBeenCalledTimes(1);
    consoleErrorSpy.mockRestore();
  });

  it("should handle non-ok HTTP response (500) by setting error state and logging to console", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useBySeasonData(10));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe("Failed to load by-season data.");
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "Error fetching by-season data:",
      expect.objectContaining({
        message: "Failed to fetch by-season data",
      }),
    );
    expect(global.fetch).toHaveBeenCalledTimes(1);
    consoleErrorSpy.mockRestore();
  });
});
