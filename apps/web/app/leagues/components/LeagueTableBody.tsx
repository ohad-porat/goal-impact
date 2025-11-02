import { tableStyles } from '../../../lib/tableStyles'
import { LeagueTableData } from '../../../lib/types'
import Link from 'next/link'

interface LeagueTableBodyProps {
  tableData: LeagueTableData
}

export function LeagueTableBody({ tableData }: LeagueTableBodyProps) {
  if (tableData.table.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={10} className={tableStyles.compact.text.center}>
            No data available
          </td>
        </tr>
      </tbody>
    )
  }

  return (
    <tbody className="bg-slate-800 divide-y divide-gray-700">
      {tableData.table.map((team, index) => (
        <tr key={team.position} className={`${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors`}>
          <td className={`${tableStyles.compact.cell} text-center w-[60px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.position}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-left w-[200px]`}>
            <Link 
              href={`/clubs/${team.team_id}/seasons?season=${tableData.season.id}`}
              className={`${tableStyles.compact.text.primary} hover:text-orange-400 transition-colors`}
            >
              {team.team_name}
            </Link>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.matches_played}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.wins}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.draws}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.losses}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.goals_for}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.goals_against}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[50px]`}>
            <span className={tableStyles.compact.text.center}>
              {team.goal_difference}
            </span>
          </td>
          <td className={`${tableStyles.compact.cell} text-center w-[60px]`}>
            <span className={tableStyles.compact.text.points}>
              {team.points}
            </span>
          </td>
        </tr>
      ))}
    </tbody>
  )
}
