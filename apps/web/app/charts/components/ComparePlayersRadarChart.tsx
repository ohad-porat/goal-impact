"use client";

import { useState, useEffect, useMemo } from "react";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { Loader2 } from "lucide-react";
import { api } from "../../../lib/api";
import { PlayerDetailsResponse } from "../../../lib/types/player";
import { SearchResult } from "../../../lib/types/search";
import { PlayerSearchInput } from "./PlayerSearchInput";
import { ErrorDisplay } from "../../../components/ErrorDisplay";

interface PlayerData {
  player: SearchResult | null;
  playerDetails: PlayerDetailsResponse | null;
  loading: boolean;
  error: string | null;
  selectedSeasonId: number | "career" | null;
}

interface RadarDataPoint {
  metric: string;
  player1: number;
  player2: number;
}

const METRICS = [
  { key: "gv_total", label: "GV Total" },
  { key: "gv_avg", label: "GV Avg" },
  { key: "goals", label: "Goals" },
  { key: "assists", label: "Assists" },
  { key: "matches_played", label: "Matches Played" },
];

const PLAYER1_COLOR = "#22c55e";
const PLAYER2_COLOR = "#3b82f6";
const NORMALIZATION_PADDING_MULTIPLIER = 1.15;

function CustomLegend({
  player1Name,
  player2Name,
}: {
  player1Name: string;
  player2Name: string;
}) {
  return (
    <div className="flex items-center justify-center gap-8">
      <div className="flex items-center gap-2">
        <div
          className="w-3 h-3 rounded-sm"
          style={{ backgroundColor: PLAYER1_COLOR }}
        />
        <span className="text-sm text-gray-300">{player1Name}</span>
      </div>
      <div className="flex items-center gap-2">
        <div
          className="w-3 h-3 rounded-sm"
          style={{ backgroundColor: PLAYER2_COLOR }}
        />
        <span className="text-sm text-gray-300">{player2Name}</span>
      </div>
    </div>
  );
}

function getPlayerStats(playerData: PlayerData): Record<string, number> | null {
  if (!playerData.playerDetails) return null;

  if (playerData.selectedSeasonId === "career") {
    const careerTotals = playerData.playerDetails.career_totals;
    return {
      gv_total: careerTotals.total_goal_value,
      gv_avg: careerTotals.goal_value_avg,
      goals: careerTotals.total_goals,
      assists: careerTotals.total_assists,
      matches_played: careerTotals.total_matches_played,
    };
  }

  if (playerData.selectedSeasonId === null) return null;

  const season = playerData.playerDetails.seasons.find(
    (s) => s.season.id === playerData.selectedSeasonId,
  );

  if (!season) return null;

  return {
    gv_total: season.stats.goal_value || 0,
    gv_avg: season.stats.gv_avg || 0,
    goals: season.stats.goals_scored || 0,
    assists: season.stats.assists || 0,
    matches_played: season.stats.matches_played || 0,
  };
}

export function ComparePlayersRadarChart() {
  const [player1, setPlayer1] = useState<PlayerData>({
    player: null,
    playerDetails: null,
    loading: false,
    error: null,
    selectedSeasonId: null,
  });

  const [player2, setPlayer2] = useState<PlayerData>({
    player: null,
    playerDetails: null,
    loading: false,
    error: null,
    selectedSeasonId: null,
  });

  useEffect(() => {
    const fetchPlayerDetails = async (
      playerId: number,
      setPlayer: React.Dispatch<React.SetStateAction<PlayerData>>,
    ) => {
      setPlayer((prev: PlayerData) => ({
        ...prev,
        loading: true,
        error: null,
      }));
      try {
        const response = await fetch(api.playerDetails(playerId), {
          cache: "no-cache",
        });
        if (!response.ok) {
          throw new Error("Failed to fetch player details");
        }
        const data: PlayerDetailsResponse = await response.json();
        setPlayer((prev: PlayerData) => ({
          ...prev,
          playerDetails: data,
          loading: false,
          selectedSeasonId: data.seasons.length > 0 ? "career" : null,
        }));
      } catch (err) {
        console.error("Error fetching player details:", err);
        setPlayer((prev: PlayerData) => ({
          ...prev,
          loading: false,
          error: "Failed to fetch player details.",
        }));
      }
    };

    if (player1.player && !player1.playerDetails && !player1.loading) {
      fetchPlayerDetails(player1.player.id, setPlayer1);
    }

    if (player2.player && !player2.playerDetails && !player2.loading) {
      fetchPlayerDetails(player2.player.id, setPlayer2);
    }
  }, [
    player1.player,
    player1.playerDetails,
    player1.loading,
    player2.player,
    player2.playerDetails,
    player2.loading,
  ]);

  const createPlayerSelectHandler =
    (setPlayer: React.Dispatch<React.SetStateAction<PlayerData>>) =>
    (player: SearchResult | null) => {
      if (!player) {
        setPlayer({
          player: null,
          playerDetails: null,
          loading: false,
          error: null,
          selectedSeasonId: null,
        });
        return;
      }
      setPlayer({
        player,
        playerDetails: null,
        loading: false,
        error: null,
        selectedSeasonId: null,
      });
    };

  const handlePlayer1Select = createPlayerSelectHandler(setPlayer1);
  const handlePlayer2Select = createPlayerSelectHandler(setPlayer2);

  const player1Stats = useMemo(() => getPlayerStats(player1), [player1]);
  const player2Stats = useMemo(() => getPlayerStats(player2), [player2]);

  const chartData: RadarDataPoint[] = useMemo(() => {
    if (!player1Stats || !player2Stats) return [];

    return METRICS.map((metric) => ({
      metric: metric.label,
      player1: player1Stats[metric.key as keyof typeof player1Stats] || 0,
      player2: player2Stats[metric.key as keyof typeof player2Stats] || 0,
    }));
  }, [player1Stats, player2Stats]);

  const normalizedChartData = useMemo(() => {
    if (chartData.length === 0) return [];

    const maxValues: Record<string, number> = {};
    METRICS.forEach((metric) => {
      const key = metric.key;
      const p1Value = player1Stats?.[key as keyof typeof player1Stats] || 0;
      const p2Value = player2Stats?.[key as keyof typeof player2Stats] || 0;
      const max = Math.max(p1Value, p2Value);
      maxValues[key] = max > 0 ? max * NORMALIZATION_PADDING_MULTIPLIER : 1;
    });

    return chartData.map((point) => {
      const metricKey =
        METRICS.find((m) => m.label === point.metric)?.key || "";
      const max = Math.max(maxValues[metricKey] || 0, 1);
      return {
        ...point,
        player1: (point.player1 / max) * 100,
        player2: (point.player2 / max) * 100,
      };
    });
  }, [chartData, player1Stats, player2Stats]);

  const canRenderChart = player1Stats !== null && player2Stats !== null;

  return (
    <div>
      <h2 className="text-xl sm:text-2xl font-bold text-white mb-6">
        Compare Players
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="space-y-4">
          <PlayerSearchInput
            label="Player 1"
            onPlayerSelect={handlePlayer1Select}
            selectedPlayer={player1.player}
          />

          {player1.loading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-6 h-6 text-green-400 animate-spin" />
            </div>
          )}

          {player1.error && <ErrorDisplay message={player1.error} />}

          {player1.playerDetails && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Season
              </label>
              <select
                value={
                  player1.selectedSeasonId === "career"
                    ? "career"
                    : player1.selectedSeasonId || ""
                }
                onChange={(e) => {
                  const value = e.target.value;
                  setPlayer1((prev) => ({
                    ...prev,
                    selectedSeasonId:
                      value === "career" ? "career" : parseInt(value, 10),
                  }));
                }}
                className="w-full px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
              >
                <option value="career">Career Totals</option>
                {player1.playerDetails.seasons.map((season, index) => (
                  <option
                    key={`player1-${season.season.id}-${index}`}
                    value={season.season.id}
                  >
                    {season.season.display_name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <PlayerSearchInput
            label="Player 2"
            onPlayerSelect={handlePlayer2Select}
            selectedPlayer={player2.player}
          />

          {player2.loading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
            </div>
          )}

          {player2.error && <ErrorDisplay message={player2.error} />}

          {player2.playerDetails && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Season
              </label>
              <select
                value={
                  player2.selectedSeasonId === "career"
                    ? "career"
                    : player2.selectedSeasonId || ""
                }
                onChange={(e) => {
                  const value = e.target.value;
                  setPlayer2((prev) => ({
                    ...prev,
                    selectedSeasonId:
                      value === "career" ? "career" : parseInt(value, 10),
                  }));
                }}
                className="w-full px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
              >
                <option value="career">Career Totals</option>
                {player2.playerDetails.seasons.map((season, index) => (
                  <option
                    key={`player2-${season.season.id}-${index}`}
                    value={season.season.id}
                  >
                    {season.season.display_name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {canRenderChart ? (
        <div
          className="bg-slate-800 rounded-lg p-4 max-w-2xl mx-auto"
          data-testid="compare-players-radar-chart"
        >
          <CustomLegend
            player1Name={player1.player?.name || "Player 1"}
            player2Name={player2.player?.name || "Player 2"}
          />
          <ResponsiveContainer width="100%" height={500}>
            <RadarChart
              data={normalizedChartData}
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              <PolarGrid stroke="#475569" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fill: "#cbd5e1", fontSize: 12 }}
              />
              <Radar
                name={player1.player?.name || "Player 1"}
                dataKey="player1"
                stroke={PLAYER1_COLOR}
                fill={PLAYER1_COLOR}
                fillOpacity={0.6}
              />
              <Radar
                name={player2.player?.name || "Player 2"}
                dataKey="player2"
                stroke={PLAYER2_COLOR}
                fill={PLAYER2_COLOR}
                fillOpacity={0.6}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #475569",
                  borderRadius: "6px",
                  color: "#e2e8f0",
                }}
                formatter={(
                  value: number | undefined,
                  name: string | undefined,
                  props: any,
                ) => {
                  const metricLabel = props.payload?.metric;
                  const playerName = name || "";
                  if (!metricLabel)
                    return [value?.toFixed(1) || "0", playerName];

                  const originalMetric = METRICS.find(
                    (m) => m.label === metricLabel,
                  );
                  if (!originalMetric)
                    return [value?.toFixed(1) || "0", playerName];

                  const metricKey = originalMetric.key;
                  let originalValue = 0;

                  if (playerName === player1.player?.name) {
                    originalValue =
                      player1Stats?.[metricKey as keyof typeof player1Stats] ||
                      0;
                  } else if (playerName === player2.player?.name) {
                    originalValue =
                      player2Stats?.[metricKey as keyof typeof player2Stats] ||
                      0;
                  }

                  return [
                    typeof originalValue === "number"
                      ? originalValue.toFixed(originalValue % 1 === 0 ? 0 : 2)
                      : String(originalValue),
                    playerName,
                  ];
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="text-center py-12 text-gray-400">
            {!player1.player && !player2.player
              ? "Select two players to compare"
              : !player1.player
                ? "Select Player 1 to compare"
                : !player2.player
                  ? "Select Player 2 to compare"
                  : "Loading player data..."}
          </div>
        </div>
      )}
    </div>
  );
}
