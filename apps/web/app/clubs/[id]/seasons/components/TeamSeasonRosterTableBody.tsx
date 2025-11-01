import { tableStyles } from '../../../../../lib/tableStyles'
import { StatCell } from '../../../../../lib/components/StatCell'
import { PlayerSeasonData } from '../../../../../lib/types/club'
import Link from 'next/link'

interface TeamSeasonRosterTableBodyProps {
  players: PlayerSeasonData[]
  seasonId?: number
  teamId?: number
  from?: string
}

export function TeamSeasonRosterTableBody({ players, seasonId, teamId, from }: TeamSeasonRosterTableBodyProps) {
  const { statsTable } = tableStyles

  if (players.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={15} className="px-6 py-8 text-center">
            <p className="text-gray-400 text-lg">No player data available</p>
          </td>
        </tr>
      </tbody>
    )
  }

  return (
    <tbody className="bg-slate-800 divide-y divide-gray-700">
      {players.map((playerData, index) => {
        const { player, stats } = playerData

        return (
          <tr key={player.id} className={`${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors`}>
            <td className={`${statsTable.cell} px-2 max-w-[320px] overflow-hidden`}>
              <Link 
                href={`/players/${player.id}?from=${from}&season=${seasonId}&teamId=${teamId}`}
                className={`${statsTable.text.primary} hover:text-orange-400 transition-colors`}
              >
                <span className="block truncate">
                  {player.name}
                </span>
              </Link>
            </td>

            <StatCell value={stats.goal_value} formatter={(v) => v.toFixed(2)} />
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
            <StatCell value={stats.total_minutes} formatter={(v) => v.toLocaleString()} />
            <StatCell value={stats.minutes_divided_90} className="border-r" />
          </tr>
        )
      })}
    </tbody>
  )
}
