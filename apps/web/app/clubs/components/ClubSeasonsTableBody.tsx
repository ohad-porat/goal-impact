import { tableStyles } from '../../../lib/tableStyles'
import { ClubSeason } from '../../../lib/types/club'

interface ClubSeasonsTableBodyProps {
  seasons: ClubSeason[]
}

export function ClubSeasonsTableBody({ seasons }: ClubSeasonsTableBodyProps) {
  if (seasons.length === 0) {
    return (
      <tbody className="bg-slate-800 divide-y divide-gray-700">
        <tr>
          <td colSpan={14} className="px-6 py-8 text-center">
            <p className="text-gray-400 text-lg">No season data available</p>
          </td>
        </tr>
      </tbody>
    )
  }

  return (
    <tbody className="bg-slate-800 divide-y divide-gray-700">
      {seasons.map((seasonData, index) => {
        const { season, competition, stats } = seasonData
        return (
          <tr key={`${season.id}-${competition.id}`} className={`${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors`}>
            <td className={`${tableStyles.compact.cell} text-left pl-6`}>
              <span className={tableStyles.compact.text.primary}>
                {season.year_range}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-left`}>
              <span className={tableStyles.compact.text.primary}>
                {competition.name}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {competition.tier || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.ranking || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.matches_played || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.wins || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.draws || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.losses || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.goals_for || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.goals_against || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.goal_difference !== null ? (stats.goal_difference > 0 ? '+' : '') + stats.goal_difference : '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.points}>
                {stats.points || '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-center`}>
              <span className={tableStyles.compact.text.center}>
                {stats.attendance ? Math.round(stats.attendance).toLocaleString() : '-'}
              </span>
            </td>
            <td className={`${tableStyles.compact.cell} text-left`}>
              <span className={tableStyles.compact.text.secondary}>
                {stats.notes || '-'}
              </span>
            </td>
          </tr>
        )
      })}
    </tbody>
  )
}
