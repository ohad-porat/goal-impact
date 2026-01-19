"use client";

import { useSearchParams, useRouter } from "next/navigation";

export function useLeaderFilters() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const selectedLeagueId = searchParams.get("league_id");
  const selectedSeasonId = searchParams.get("season_id");

  const leagueId =
    selectedLeagueId && !isNaN(parseInt(selectedLeagueId, 10))
      ? parseInt(selectedLeagueId, 10)
      : undefined;

  const seasonId =
    selectedSeasonId && !isNaN(parseInt(selectedSeasonId, 10))
      ? parseInt(selectedSeasonId, 10)
      : undefined;

  const updateParams = (
    view: string,
    updates: Record<string, string | null>,
  ) => {
    const params = new URLSearchParams(searchParams.toString());
    if (!params.get("view")) {
      params.set("view", view);
    }

    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });

    router.push(`/leaders?${params.toString()}`, { scroll: false });
  };

  return {
    leagueId,
    seasonId,
    selectedLeagueId,
    selectedSeasonId,
    updateParams,
  };
}
