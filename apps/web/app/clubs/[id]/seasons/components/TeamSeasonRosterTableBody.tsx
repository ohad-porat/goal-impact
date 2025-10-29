import { tableStyles } from '../../../../../lib/tableStyles'
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
            
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.goal_value !== null ? stats.goal_value.toFixed(2) : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.gv_avg !== null ? stats.gv_avg.toFixed(2) : '-'}
              </span>
            </td>
            
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.goals_scored !== null ? stats.goals_scored : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.assists !== null ? stats.assists : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.total_goal_assists !== null ? stats.total_goal_assists : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.non_pk_goals !== null ? stats.non_pk_goals : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.pk_made !== null ? stats.pk_made : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.pk_attempted !== null ? stats.pk_attempted : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.yellow_cards !== null ? stats.yellow_cards : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.red_cards !== null ? stats.red_cards : '-'}
              </span>
            </td>
            
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.matches_played !== null ? stats.matches_played : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.matches_started !== null ? stats.matches_started : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell}`}>
              <span className={statsTable.text.center}>
                {stats.total_minutes !== null ? stats.total_minutes.toLocaleString() : '-'}
              </span>
            </td>
            <td className={`${statsTable.cell} border-r`}>
              <span className={statsTable.text.center}>
                {stats.minutes_divided_90 !== null ? stats.minutes_divided_90 : '-'}
              </span>
            </td>
          </tr>
        )
      })}
    </tbody>
  )
}
