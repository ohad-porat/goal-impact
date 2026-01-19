"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "../../../lib/api";
import { Season } from "../../../lib/types";

export function useSeasons(leagueId?: number) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSeasons = async () => {
      setLoading(true);
      try {
        const url = leagueId ? api.leagueSeasons(leagueId) : api.allSeasons;
        const response = await fetch(url, { cache: "no-cache" });
        if (!response.ok) {
          throw new Error("Failed to fetch seasons");
        }
        const data = await response.json();
        setSeasons(data.seasons || []);

        const currentSeasonId = searchParams.get("season_id");
        if (!currentSeasonId && data.seasons && data.seasons.length > 0) {
          const mostRecentSeason = data.seasons[0];
          const params = new URLSearchParams(searchParams.toString());
          params.set("season_id", mostRecentSeason.id.toString());
          if (!params.get("view")) {
            params.set("view", "by-season");
          }
          router.push(`/leaders?${params.toString()}`, { scroll: false });
        }
      } catch (err) {
        console.error("Error fetching seasons:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSeasons();
  }, [leagueId, searchParams, router]);

  return { seasons, loading };
}
