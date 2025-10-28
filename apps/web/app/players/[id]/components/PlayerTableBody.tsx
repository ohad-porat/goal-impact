import { tableStyles } from '../../../../lib/tableStyles'
import { PlayerSeasonRecord } from '../../../../lib/types/player'
import { getShortLeagueName } from '../../../../lib/utils'
import Link from 'next/link'

interface PlayerTableBodyProps {
  seasons: PlayerSeasonRecord[]
}

export function PlayerTableBody({ seasons }: PlayerTableBodyProps) {
  const { teamSeason } = tableStyles
  
  if (seasons.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={23} className="px-6 py-8 text-center">
            <p className="text-gray-400 text-lg">No season data available</p>
          </td>
        </tr>
      </tbody>
    )
  }

  return (
    <tbody className="bg-slate-800 divide-y divide-gray-700">
      {seasons.map((seasonData, index) => {
        const { season, team, competition, league_rank, stats } = seasonData
        
        return (
          <tr key={`${season.id}-${team.id}`} className={`${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors`}>
            <td className={`${teamSeason.cell} text-center px-2 w-[120px]`}>
              <span className={teamSeason.text.primary}>
                {season.display_name}
              </span>
            </td>
            
            <td className={`${teamSeason.cell} text-center px-2 w-[200px]`}>
              <Link 
                href={`/clubs/${team.id}/seasons?season=${season.id}`}
                className={`${teamSeason.text.primary} hover:text-orange-400 transition-colors`}
              >
                {team.name}
              </Link>
            </td>
            
            <td className={`${teamSeason.cell} text-center px-2 w-[150px]`}>
              <span className={teamSeason.text.primary}>
                {getShortLeagueName(competition.name)}
              </span>
            </td>
            
            <td className={`${teamSeason.cell} text-center w-[80px]`}>
              <span className={teamSeason.text.center}>
                {league_rank !== null ? league_rank : '-'}
              </span>
            </td>
            
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.goal_value !== null ? stats.goal_value.toFixed(2) : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.gv_avg !== null ? stats.gv_avg.toFixed(2) : '-'}
              </span>
            </td>
            
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.goals_scored !== null ? stats.goals_scored : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.assists !== null ? stats.assists : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.total_goal_assists !== null ? stats.total_goal_assists : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.non_pk_goals !== null ? stats.non_pk_goals : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.pk_made !== null ? stats.pk_made : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.pk_attempted !== null ? stats.pk_attempted : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.yellow_cards !== null ? stats.yellow_cards : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.red_cards !== null ? stats.red_cards : '-'}
              </span>
            </td>
            
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.goal_per_90 !== null ? stats.goal_per_90.toFixed(2) : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.assists_per_90 !== null ? stats.assists_per_90.toFixed(2) : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.total_goals_assists_per_90 !== null ? stats.total_goals_assists_per_90.toFixed(2) : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.non_pk_goals_per_90 !== null ? stats.non_pk_goals_per_90.toFixed(2) : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[90px]`}>
              <span className={teamSeason.text.center}>
                {stats.non_pk_goal_and_assists_per_90 !== null ? stats.non_pk_goal_and_assists_per_90.toFixed(2) : '-'}
              </span>
            </td>
            
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.matches_played !== null ? stats.matches_played : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.matches_started !== null ? stats.matches_started : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.total_minutes !== null ? stats.total_minutes.toLocaleString() : '-'}
              </span>
            </td>
            <td className={`${teamSeason.cell} text-center border-r w-[85px]`}>
              <span className={teamSeason.text.center}>
                {stats.minutes_divided_90 !== null ? stats.minutes_divided_90 : '-'}
              </span>
            </td>
          </tr>
        )
      })}
    </tbody>
  )
}
