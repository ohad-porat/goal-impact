import { tableStyles } from "../../../../../../lib/tableStyles";
import { StatCell } from "../../../../../../lib/components/StatCell";
import { GoalLogEntry } from "../../../../../../lib/types/club";
import Link from "next/link";

interface TeamSeasonGoalLogTableBodyProps {
  goals: GoalLogEntry[];
}

export function TeamSeasonGoalLogTableBody({
  goals,
}: TeamSeasonGoalLogTableBodyProps) {
  const { statsTable } = tableStyles;

  if (goals.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={10} className="px-6 py-8 text-center">
            <p className="text-gray-400 text-lg">
              No goals found for this season
            </p>
          </td>
        </tr>
      </tbody>
    );
  }

  return (
    <tbody className="bg-slate-800">
      {goals.map((goal, index) => {
        const previousGoal = index > 0 ? goals[index - 1] : null;
        const isDateChange = previousGoal && previousGoal.date !== goal.date;
        const borderClass = isDateChange
          ? "border-t-2 border-gray-500"
          : index > 0
            ? "border-t border-gray-700"
            : "";

        return (
          <tr
            key={`${goal.date}-${goal.minute}-${goal.scorer.id}`}
            className={`${index % 2 === 0 ? "bg-slate-800" : "bg-slate-750"} hover:bg-slate-700 transition-colors ${borderClass}`}
          >
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>{goal.date}</span>
            </td>

            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>{goal.venue}</span>
            </td>

            <td
              className={`${statsTable.cell} px-2 max-w-[180px] overflow-hidden`}
            >
              <Link
                href={`/players/${goal.scorer.id}`}
                className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
              >
                <span className="block truncate">{goal.scorer.name}</span>
              </Link>
            </td>

            <td
              className={`${statsTable.cell} px-2 max-w-[180px] overflow-hidden`}
            >
              <Link
                href={`/clubs/${goal.opponent.id}`}
                className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
              >
                <span className="block truncate">{goal.opponent.name}</span>
              </Link>
            </td>

            <StatCell value={goal.minute} />

            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {goal.score_before} → {goal.score_after}
              </span>
            </td>

            <StatCell value={goal.goal_value} formatter={(v) => v.toFixed(2)} />

            <StatCell value={goal.xg} formatter={(v) => v.toFixed(2)} />

            <StatCell
              value={goal.post_shot_xg}
              formatter={(v) => v.toFixed(2)}
            />

            <td
              className={`${statsTable.cell} px-2 max-w-[180px] overflow-hidden border-r`}
            >
              {goal.assisted_by ? (
                <Link
                  href={`/players/${goal.assisted_by.id}`}
                  className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
                >
                  <span className="block truncate">
                    {goal.assisted_by.name}
                  </span>
                </Link>
              ) : (
                <span className={statsTable.text.center}>-</span>
              )}
            </td>
          </tr>
        );
      })}
    </tbody>
  );
}
