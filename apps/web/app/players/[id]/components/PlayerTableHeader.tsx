import React from "react";
import { tableStyles } from "../../../../lib/tableStyles";

export function PlayerTableHeader() {
  const { statsTable } = tableStyles;

  return (
    <thead className="bg-gray-700">
      <tr>
        <th rowSpan={2} className={`${statsTable.headerLeft} pl-3 w-[100px]`}>
          Season
        </th>
        <th rowSpan={2} className={`${statsTable.headerLeft} pl-3 w-[170px]`}>
          Team
        </th>
        <th rowSpan={2} className={`${statsTable.headerLeft} pl-3 w-[140px]`}>
          League
        </th>
        <th rowSpan={2} className={`${statsTable.headerBottom} w-[70px]`}>
          LgRnk
        </th>
        <th colSpan={2} className={`${statsTable.headerBottom}`}>
          Goal Value
        </th>
        <th colSpan={8} className={`${statsTable.headerBottom}`}>
          Performance
        </th>
        <th
          colSpan={4}
          className={`${statsTable.header} border-b border-gray-600`}
        >
          Playing Time
        </th>
      </tr>

      <tr>
        <th className={`${statsTable.header} w-[60px]`}>Total</th>
        <th className={`${statsTable.header} w-[60px]`}>Avg</th>

        <th className={`${statsTable.header} w-[60px]`}>Gls</th>
        <th className={`${statsTable.header} w-[60px]`}>Ast</th>
        <th className={`${statsTable.header} w-[60px]`}>G+A</th>
        <th className={`${statsTable.header} w-[60px]`}>G-PK</th>
        <th className={`${statsTable.header} w-[60px]`}>PK</th>
        <th className={`${statsTable.header} w-[60px]`}>PK att</th>
        <th className={`${statsTable.header} w-[60px]`}>Yellow</th>
        <th className={`${statsTable.header} w-[60px]`}>Red</th>

        <th className={`${statsTable.header} w-[60px]`}>MP</th>
        <th className={`${statsTable.header} w-[60px]`}>Starts</th>
        <th className={`${statsTable.header} w-[60px]`}>Min</th>
        <th className={`${statsTable.header} border-r-0 w-[60px]`}>90s</th>
      </tr>
    </thead>
  );
}
