import { tableStyles } from '../../../../../lib/tableStyles'
import { StatCell } from '../../../../../lib/components/StatCell'
import { PlayerGoalLogEntry } from '../../../../../lib/types/club'
import Link from 'next/link'

interface PlayerGoalLogTableBodyProps {
  goals: PlayerGoalLogEntry[]
}

export function PlayerGoalLogTableBody({ goals }: PlayerGoalLogTableBodyProps) {
  const { statsTable } = tableStyles

  if (goals.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={10} className="px-6 py-8 text-center">
            <p className="text-gray-400 text-lg">No goals found for this player</p>
          </td>
        </tr>
      </tbody>
    )
  }

  const rows: Array<{ type: 'goal' | 'season', data: PlayerGoalLogEntry | { season_id: number, display_name: string } }> = []
  let currentSeasonDisplayName: string | null = null

  goals.forEach((goal) => {
    if (goal.season_display_name !== currentSeasonDisplayName) {
      rows.push({
        type: 'season',
        data: {
          season_id: goal.season_id,
          display_name: goal.season_display_name
        }
      })
      currentSeasonDisplayName = goal.season_display_name
    }
    rows.push({ type: 'goal', data: goal })
  })

  return (
    <tbody className="bg-slate-800">
      {rows.map((row, index) => {
        if (row.type === 'season') {
          const seasonData = row.data as { season_id: number, display_name: string }
          return (
            <tr key={`season-${seasonData.season_id}`} className="bg-gray-700 border-t-2 border-gray-600">
              <td colSpan={10} className="px-3 py-1.5 text-center">
                <span className="text-base font-bold text-white">
                  {seasonData.display_name}
                </span>
              </td>
            </tr>
          )
        }

        const goal = row.data as PlayerGoalLogEntry
        const goalIndex = rows.slice(0, index).filter(r => r.type === 'goal').length
        
        return (
          <tr 
            key={`${goal.date}-${goal.minute}-${goal.team.id}`} 
            className={`${goalIndex % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors border-t border-gray-700`}
          >
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {goal.date}
              </span>
            </td>
            
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {goal.venue}
              </span>
            </td>

            <td className={`${statsTable.cell} px-2 max-w-[180px] overflow-hidden`}>
              <Link 
                href={`/clubs/${goal.team.id}`}
                className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
              >
                <span className="block truncate">
                  {goal.team.name}
                </span>
              </Link>
            </td>

            <td className={`${statsTable.cell} px-2 max-w-[180px] overflow-hidden`}>
              <Link 
                href={`/clubs/${goal.opponent.id}`}
                className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
              >
                <span className="block truncate">
                  {goal.opponent.name}
                </span>
              </Link>
            </td>

            <StatCell value={goal.minute} />

            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {goal.score_before} → {goal.score_after}
              </span>
            </td>

            <StatCell 
              value={goal.goal_value} 
              formatter={(v) => v.toFixed(2)} 
            />

            <StatCell 
              value={goal.xg} 
              formatter={(v) => v.toFixed(2)} 
            />

            <StatCell 
              value={goal.post_shot_xg} 
              formatter={(v) => v.toFixed(2)} 
            />

            <td className={`${statsTable.cell} px-2 max-w-[180px] overflow-hidden border-r`}>
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
        )
      })}
    </tbody>
  )
}
