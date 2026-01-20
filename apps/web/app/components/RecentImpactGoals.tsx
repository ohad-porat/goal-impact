"use client";

import { useState, useEffect } from "react";
import { RecentImpactGoalsResponse } from "../../lib/types/home";
import { League } from "../../lib/types/league";
import { api } from "../../lib/api";
import { getShortLeagueName } from "../../lib/utils";

interface RecentImpactGoalsProps {
  initialLeagues: League[];
  initialGoals: RecentImpactGoalsResponse | null;
}

function formatGoalValue(value: number): string {
  return `+${value.toFixed(2)}`;
}

const TOP_LEAGUE_ORDER = ["Premier League", "Serie A", "La Liga", "Bundesliga"];

export function RecentImpactGoals({
  initialLeagues,
  initialGoals,
}: RecentImpactGoalsProps) {
  const [selectedLeagueId, setSelectedLeagueId] = useState<number | undefined>(
    undefined,
  );
  const [goalsData, setGoalsData] = useState<RecentImpactGoalsResponse | null>(
    initialGoals,
  );
  const [error, setError] = useState<string | null>(null);

  const topLeagues = initialLeagues
    .filter((league) => {
      const normalized = getShortLeagueName(league.name);
      return TOP_LEAGUE_ORDER.includes(normalized);
    })
    .sort((a, b) => {
      const nameA = getShortLeagueName(a.name);
      const nameB = getShortLeagueName(b.name);
      const orderA = TOP_LEAGUE_ORDER.indexOf(nameA);
      const orderB = TOP_LEAGUE_ORDER.indexOf(nameB);
      if (orderA === -1 && orderB === -1) return 0;
      if (orderA === -1) return 1;
      if (orderB === -1) return -1;
      return orderA - orderB;
    })
    .slice(0, 4);

  useEffect(() => {
    if (selectedLeagueId === undefined) {
      setGoalsData(initialGoals);
      setError(null);
      return;
    }

    async function fetchGoals() {
      setError(null);
      try {
        const response = await fetch(api.recentGoals(selectedLeagueId), {
          cache: "no-cache",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch recent goals");
        }

        const data = await response.json();
        setGoalsData(data);
      } catch (err) {
        setError("Failed to load recent goals.");
        setGoalsData(null);
      }
    }

    fetchGoals();
  }, [selectedLeagueId, initialGoals]);

  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 sm:mb-8">
        <h2 className="text-2xl sm:text-3xl font-bold text-orange-400">
          Recent Impact Goals
        </h2>

        <div className="w-full sm:w-auto">
          <select
            value={selectedLeagueId?.toString() || ""}
            onChange={(e) =>
              setSelectedLeagueId(
                e.target.value ? parseInt(e.target.value) : undefined,
              )
            }
            className="w-full md:hidden px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
          >
            <option value="">All Leagues</option>
            {topLeagues.map((league) => (
              <option key={league.id} value={league.id.toString()}>
                {getShortLeagueName(league.name)}
              </option>
            ))}
          </select>

          <div className="hidden md:flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setSelectedLeagueId(undefined)}
              className={`px-4 py-2 rounded-md font-semibold text-sm transition-colors whitespace-nowrap ${
                selectedLeagueId === undefined
                  ? "bg-orange-400 text-black"
                  : "bg-slate-700 text-white hover:bg-slate-600"
              }`}
            >
              All Leagues
            </button>
            {topLeagues.map((league) => (
              <button
                key={league.id}
                onClick={() => setSelectedLeagueId(league.id)}
                className={`px-4 py-2 rounded-md font-semibold text-sm transition-colors whitespace-nowrap ${
                  selectedLeagueId === league.id
                    ? "bg-orange-400 text-black"
                    : "bg-slate-700 text-white hover:bg-slate-600"
                }`}
              >
                {getShortLeagueName(league.name)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error ? (
        <div className="bg-gray-800 rounded-lg shadow-lg p-8 text-center">
          <p className="text-gray-400 text-lg">{error}</p>
        </div>
      ) : goalsData && goalsData.goals.length === 0 ? (
        <div className="bg-gray-800 rounded-lg shadow-lg p-8 text-center">
          <p className="text-gray-400 text-lg">No recent goals found</p>
        </div>
      ) : goalsData ? (
        <div className="space-y-2">
          {goalsData.goals.map((goal, index) => (
            <div
              key={index}
              className="bg-gray-50 rounded-lg shadow-lg p-2.5 md:p-4 grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_1fr] gap-2 md:gap-4"
            >
              <div className="flex flex-col justify-start md:justify-start">
                <p className="text-gray-900 font-semibold text-sm md:text-base leading-tight">
                  {goal.match.home_team} vs {goal.match.away_team}
                </p>
                <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 mt-0.5 md:hidden">
                  <p className="text-gray-600 text-xs">{goal.match.date}</p>
                  <span className="text-gray-400 text-xs">•</span>
                  <p className="text-gray-900 font-medium text-xs">
                    {goal.scorer.name}
                  </p>
                  <span className="text-gray-400 text-xs">•</span>
                  <p className="text-gray-700 text-xs">Minute {goal.minute}</p>
                </div>
                <p className="text-gray-600 text-xs mt-1 hidden md:block">
                  {goal.match.date}
                </p>
              </div>

              <div className="hidden md:flex flex-col justify-start">
                <p className="text-gray-700 text-xs font-semibold mb-1">
                  Minute {goal.minute}
                </p>
                <p className="text-gray-900 font-medium text-sm md:text-base leading-tight">
                  {goal.scorer.name}
                </p>
              </div>

              <div className="flex items-center gap-2 md:flex-col md:justify-start md:items-start">
                <div className="flex items-center gap-1.5 md:flex-col md:items-start">
                  <span className="text-gray-700 text-xs font-semibold md:mb-1">
                    Score:
                  </span>
                  {goal.score_before && goal.score_after ? (
                    <span className="text-gray-700 text-sm md:block leading-tight">
                      {goal.score_before} → {goal.score_after}
                    </span>
                  ) : (
                    <span className="text-gray-400 text-sm md:block">-</span>
                  )}
                </div>
                <span className="text-gray-400 text-xs md:hidden">•</span>
                <div className="flex items-center gap-1.5 md:hidden">
                  <span className="text-gray-700 text-xs font-semibold">
                    GV:
                  </span>
                  <span className="text-gray-900 font-bold text-sm leading-tight">
                    {formatGoalValue(goal.goal_value)}
                  </span>
                </div>
              </div>

              <div className="hidden md:flex flex-col justify-start items-end md:items-start">
                <p className="text-gray-700 text-xs font-semibold mb-1">GV</p>
                <p className="text-gray-900 font-bold text-base md:text-lg leading-tight">
                  {formatGoalValue(goal.goal_value)}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
