import { tableStyles } from "../../../lib/tableStyles";

export function LeagueTableHeader() {
  return (
    <thead className="bg-orange-400">
      <tr>
        <th className={`${tableStyles.compact.header} w-[60px]`}>Pos</th>
        <th className={`${tableStyles.compact.headerLeft} w-[200px]`}>Club</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>MP</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>W</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>D</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>L</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>GF</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>GA</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>GD</th>
        <th className={`${tableStyles.compact.header} w-[60px]`}>Pts</th>
      </tr>
    </thead>
  );
}
