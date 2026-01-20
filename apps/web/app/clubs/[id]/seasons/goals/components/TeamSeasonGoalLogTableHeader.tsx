import { tableStyles } from "../../../../../../lib/tableStyles";

export function TeamSeasonGoalLogTableHeader() {
  const { statsTable } = tableStyles;

  return (
    <thead className="bg-gray-700">
      <tr>
        <th className={`${statsTable.header} w-[100px]`}>Date</th>
        <th className={`${statsTable.header} w-[80px]`}>Venue</th>
        <th className={`${statsTable.headerLeft} pl-3 w-[180px]`}>Scorer</th>
        <th className={`${statsTable.headerLeft} pl-3 w-[180px]`}>Opponent</th>
        <th className={`${statsTable.header} w-[70px]`}>Minute</th>
        <th className={`${statsTable.header} w-[120px]`}>Score</th>
        <th className={`${statsTable.header} w-[80px]`}>Goal Value</th>
        <th className={`${statsTable.header} w-[70px]`}>xG</th>
        <th className={`${statsTable.header} w-[80px]`}>PSxG</th>
        <th className={`${statsTable.headerLeft} pl-3 border-r-0 w-[180px]`}>
          Assisted By
        </th>
      </tr>
    </thead>
  );
}
