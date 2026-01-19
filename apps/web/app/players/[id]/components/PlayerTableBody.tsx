"use client";

import { useState, useRef } from "react";
import { tableStyles } from "../../../../lib/tableStyles";
import { StatCell } from "../../../../lib/components/StatCell";
import { PlayerSeasonRecord } from "../../../../lib/types/player";
import { getShortLeagueName } from "../../../../lib/utils";
import Link from "next/link";

interface PlayerTableBodyProps {
  seasons: PlayerSeasonRecord[];
}

export function PlayerTableBody({ seasons }: PlayerTableBodyProps) {
  const { statsTable } = tableStyles;
  const [hoveredSeasonGroup, setHoveredSeasonGroup] = useState<string | null>(
    null,
  );
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  if (seasons.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={18} className="px-6 py-8 text-center">
            <p className="text-gray-400 text-lg">No season data available</p>
          </td>
        </tr>
      </tbody>
    );
  }

  const getSeasonName = (index: number) => seasons[index].season.display_name;

  const getSeasonRowSpan = (currentIndex: number): number => {
    const currentSeasonName = getSeasonName(currentIndex);
    let rowSpan = 1;

    for (let i = currentIndex + 1; i < seasons.length; i++) {
      if (getSeasonName(i) === currentSeasonName) {
        rowSpan++;
      } else {
        break;
      }
    }

    return rowSpan;
  };

  const getSeasonGroupClass = (seasonName: string) =>
    `season-group-${seasonName.replace(/[^a-zA-Z0-9]/g, "-")}`;

  const handleMouseEnter = (group: string) => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
    setHoveredSeasonGroup(group);
  };

  const handleMouseLeave = () => {
    hoverTimeoutRef.current = setTimeout(() => setHoveredSeasonGroup(null), 50);
  };

  return (
    <tbody className="bg-slate-800 divide-y divide-gray-700">
      {seasons.map((seasonData, index) => {
        const { season, team, competition, league_rank, stats } = seasonData;
        const isFirstOccurrence =
          index === 0 || getSeasonName(index) !== getSeasonName(index - 1);
        const rowSpan = isFirstOccurrence ? getSeasonRowSpan(index) : undefined;
        const seasonGroupClass = getSeasonGroupClass(getSeasonName(index));
        const isHovered = hoveredSeasonGroup === seasonGroupClass;
        const rowBg = isHovered
          ? "bg-slate-700"
          : index % 2 === 0
            ? "bg-slate-800"
            : "bg-slate-750";

        return (
          <tr
            key={`${season.id}-${team.id}`}
            className={`${seasonGroupClass} ${rowBg} transition-colors`}
            onMouseEnter={() => handleMouseEnter(seasonGroupClass)}
            onMouseLeave={handleMouseLeave}
          >
            {isFirstOccurrence && (
              <td
                rowSpan={rowSpan}
                className={`${statsTable.cell} px-2 align-middle transition-colors${isHovered ? " bg-slate-700" : ""}`}
              >
                <span className={statsTable.text.primary}>
                  {season.display_name}
                </span>
              </td>
            )}

            <td
              className={`${statsTable.cell} px-2 max-w-[170px] overflow-hidden`}
            >
              <Link
                href={`/clubs/${team.id}/seasons?season=${season.id}`}
                className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
              >
                <span className="block truncate">{team.name}</span>
              </Link>
            </td>

            <td
              className={`${statsTable.cell} px-2 max-w-[140px] overflow-hidden`}
            >
              <span className={`${statsTable.text.primary} block truncate`}>
                {getShortLeagueName(competition.name)}
              </span>
            </td>

            <StatCell value={league_rank} />
            <StatCell
              value={stats.goal_value}
              formatter={(v) => v.toFixed(2)}
            />
            <StatCell value={stats.gv_avg} formatter={(v) => v.toFixed(2)} />
            <StatCell value={stats.goals_scored} />
            <StatCell value={stats.assists} />
            <StatCell value={stats.total_goal_assists} />
            <StatCell value={stats.non_pk_goals} />
            <StatCell value={stats.pk_made} />
            <StatCell value={stats.pk_attempted} />
            <StatCell value={stats.yellow_cards} />
            <StatCell value={stats.red_cards} />
            <StatCell value={stats.matches_played} />
            <StatCell value={stats.matches_started} />
            <StatCell
              value={stats.total_minutes}
              formatter={(v) => v.toLocaleString()}
            />
            <StatCell value={stats.minutes_divided_90} className="border-r" />
          </tr>
        );
      })}
    </tbody>
  );
}
