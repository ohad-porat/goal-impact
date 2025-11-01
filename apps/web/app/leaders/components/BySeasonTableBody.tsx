import { tableStyles } from '../../../lib/tableStyles'
import { StatCell } from '../../../lib/components/StatCell'
import { BySeasonPlayer } from '../../../lib/types/leaders'
import Link from 'next/link'

interface BySeasonTableBodyProps {
  players: BySeasonPlayer[]
}

export function BySeasonTableBody({ players }: BySeasonTableBodyProps) {
  if (players.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={7} className={tableStyles.compact.text.center}>
            No data available
          </td>
        </tr>
      </tbody>
    )
  }

  return (
    <tbody className="bg-slate-800 divide-y divide-gray-700">
      {players.map((player, index) => (
        <tr 
          key={player.player_id} 
          className={`${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors`}
        >
          <td className={`${tableStyles.compact.cell} text-center w-[60px]`}>
            <span className={tableStyles.compact.text.center}>
              {index + 1}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-left w-[250px]`}>
            <Link 
              href={`/players/${player.player_id}`}
              className={`${tableStyles.compact.text.primary} hover:text-orange-400 transition-colors`}
            >
              {player.player_name}
            </Link>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[200px] px-2`}>
            <span 
              className={`${tableStyles.compact.text.center} block truncate`}
              title={player.clubs}
            >
              {player.clubs}
            </span>
          </td>
          <StatCell 
            value={player.total_goal_value} 
            formatter={(v) => v.toFixed(2)} 
            style="compact"
            className="w-[100px]"
          />
          <StatCell 
            value={player.goal_value_avg} 
            formatter={(v) => v.toFixed(2)} 
            style="compact"
            className="w-[100px]"
          />
          <StatCell 
            value={player.total_goals} 
            style="compact"
            className="w-[80px]"
          />
          <StatCell 
            value={player.total_matches} 
            style="compact"
            className="w-[80px]"
          />
        </tr>
      ))}
    </tbody>
  )
}

