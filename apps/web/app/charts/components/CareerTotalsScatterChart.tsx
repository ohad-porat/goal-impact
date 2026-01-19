"use client";

import { useState, useEffect, useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { TooltipProps } from "recharts";
import { Loader2 } from "lucide-react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "../../../lib/api";
import { CareerTotalsResponse } from "../../../lib/types/leaders";
import { ScatterChartDataPoint } from "../../../lib/types/charts";
import { getShortLeagueName } from "../../../lib/utils";
import { useLeagues } from "../../leaders/hooks/useLeagues";
import { ErrorDisplay } from "../../../components/ErrorDisplay";

const CHART_COLOR = "#f97316";

type CustomTooltipProps = TooltipProps<number, string> & {
  payload?: Array<{
    payload: ScatterChartDataPoint;
  }>;
};

export function CareerTotalsScatterChart() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { leagues, loading: loadingLeagues } = useLeagues();
  const [careerTotals, setCareerTotals] = useState<CareerTotalsResponse | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const selectedLeagueId = searchParams.get("league_id");
  const leagueId =
    selectedLeagueId && !isNaN(parseInt(selectedLeagueId, 10))
      ? parseInt(selectedLeagueId, 10)
      : undefined;

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setCareerTotals(null);
      setError(null);

      try {
        const response = await fetch(api.leadersCareerTotals(leagueId), {
          cache: "no-cache",
        });
        if (!response.ok) {
          throw new Error("Failed to fetch career totals");
        }
        const data = await response.json();
        setCareerTotals(data);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to load career totals data.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [leagueId]);

  const chartData: ScatterChartDataPoint[] = useMemo(() => {
    if (!careerTotals) return [];
    return careerTotals.top_goal_value.map((player) => ({
      x: player.total_goals,
      y: player.total_goal_value,
      playerId: player.player_id,
      playerName: player.player_name,
    }));
  }, [careerTotals]);

  const { xDomain, yDomain } = useMemo(() => {
    if (chartData.length === 0) {
      return { xDomain: [0, 100], yDomain: [0, 100] };
    }

    const xValues = chartData.map((d) => d.x);
    const yValues = chartData.map((d) => d.y);

    const xMin = Math.min(...xValues);
    const xMax = Math.max(...xValues);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);

    const xPadding = (xMax - xMin) * 0.05;
    const yPadding = (yMax - yMin) * 0.05;

    return {
      xDomain: [
        Math.max(0, Math.floor(xMin - xPadding)),
        Math.ceil(xMax + xPadding),
      ],
      yDomain: [
        Math.max(0, Math.floor(yMin - yPadding)),
        Math.ceil(yMax + yPadding),
      ],
    };
  }, [chartData]);

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const params = new URLSearchParams(searchParams.toString());
    const newLeagueId = event.target.value === "" ? null : event.target.value;

    if (newLeagueId) {
      params.set("league_id", newLeagueId);
    } else {
      params.delete("league_id");
    }

    router.push(`/charts?${params.toString()}`, { scroll: false });
  };

  const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload as ScatterChartDataPoint;
      return (
        <div className="bg-slate-800 p-3 rounded-md border border-slate-600 shadow-lg">
          <p className="text-white font-semibold">{data.playerName}</p>
          <p className="text-gray-300 text-sm">GV Total: {data.y.toFixed(2)}</p>
          <p className="text-gray-300 text-sm">Total Goals: {data.x}</p>
        </div>
      );
    }
    return null;
  };

  if (loading || loadingLeagues) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-12 h-12 text-orange-400 animate-spin" />
      </div>
    );
  }

  if (error) {
    return <ErrorDisplay message={error} />;
  }

  const isEmpty = careerTotals !== null && chartData.length === 0;

  return (
    <div>
      <div className="mb-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 className="text-xl sm:text-2xl font-bold text-white">
          Career Totals Scatter Chart
        </h2>
        <select
          id="league-filter"
          value={selectedLeagueId || ""}
          onChange={handleLeagueChange}
          className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent w-full sm:w-auto"
          disabled={loadingLeagues}
        >
          <option value="">All Leagues</option>
          {leagues.map((league) => (
            <option key={league.id} value={league.id.toString()}>
              {getShortLeagueName(league.name)}
            </option>
          ))}
        </select>
      </div>
      {isEmpty ? (
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="text-center py-12 text-gray-400">
            No data available for the selected league.
          </div>
        </div>
      ) : (
        <div
          className="bg-slate-800 rounded-lg p-4"
          data-testid="career-totals-scatter-chart"
        >
          <ResponsiveContainer width="100%" height={500}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis
                type="number"
                dataKey="x"
                name="Total Goals"
                domain={xDomain}
                label={{
                  value: "Total Goals",
                  position: "insideBottom",
                  offset: -5,
                  style: { fill: "#e2e8f0" },
                }}
                stroke="#cbd5e1"
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Total Goal Value"
                domain={yDomain}
                label={{
                  value: "Total Goal Value",
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "#e2e8f0" },
                }}
                stroke="#cbd5e1"
              />
              <Tooltip content={<CustomTooltip />} animationDuration={0} />
              <Scatter name="Players" data={chartData} fill={CHART_COLOR} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
