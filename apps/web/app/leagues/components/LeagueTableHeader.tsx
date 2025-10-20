import { tableStyles } from '../../../lib/tableStyles'

export function LeagueTableHeader() {
  return (
    <thead className="bg-orange-400">
      <tr>
        <th className={tableStyles.compact.header}>Pos</th>
        <th className={tableStyles.compact.headerLeft}>Club</th>
        <th className={tableStyles.compact.header}>MP</th>
        <th className={tableStyles.compact.header}>W</th>
        <th className={tableStyles.compact.header}>D</th>
        <th className={tableStyles.compact.header}>L</th>
        <th className={tableStyles.compact.header}>GF</th>
        <th className={tableStyles.compact.header}>GA</th>
        <th className={tableStyles.compact.header}>GD</th>
        <th className={tableStyles.compact.header}>Pts</th>
      </tr>
    </thead>
  )
}
