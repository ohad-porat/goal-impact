import { tableStyles } from '../../../lib/tableStyles'
import { CareerTotalsPlayer } from '../../../lib/types/leaders'
import Link from 'next/link'

interface CareerTotalsTableBodyProps {
  players: CareerTotalsPlayer[]
}

export function CareerTotalsTableBody({ players }: CareerTotalsTableBodyProps) {
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
          <td className={`${tableStyles.compact.cell} text-center w-[120px]`}>
            <span className={tableStyles.compact.text.center}>
              {player.nation?.name || '-'}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[100px]`}>
            <span className={tableStyles.compact.text.center}>
              {player.total_goal_value.toFixed(2)}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[100px]`}>
            <span className={tableStyles.compact.text.center}>
              {player.goal_value_avg.toFixed(2)}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[80px]`}>
            <span className={tableStyles.compact.text.center}>
              {player.total_goals}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[80px]`}>
            <span className={tableStyles.compact.text.center}>
              {player.total_matches}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  )
}

