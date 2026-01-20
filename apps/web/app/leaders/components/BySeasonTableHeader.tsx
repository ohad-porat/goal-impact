import { tableStyles } from "../../../lib/tableStyles";

export function BySeasonTableHeader() {
  return (
    <thead className="bg-orange-400">
      <tr>
        <th className={`${tableStyles.compact.header} w-[60px]`}>Rank</th>
        <th className={`${tableStyles.compact.headerLeft} w-[250px]`}>
          Player
        </th>
        <th className={`${tableStyles.compact.header} w-[200px]`}>Club</th>
        <th className={`${tableStyles.compact.header} w-[100px]`}>GV</th>
        <th className={`${tableStyles.compact.header} w-[100px]`}>GV Avg</th>
        <th className={`${tableStyles.compact.header} w-[80px]`}>Goals</th>
        <th className={`${tableStyles.compact.header} w-[80px]`}>Matches</th>
      </tr>
    </thead>
  );
}
