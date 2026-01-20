import { tableStyles } from "../../../lib/tableStyles";

export function ClubSeasonsTableHeader() {
  return (
    <thead className="bg-orange-400">
      <tr>
        <th className={`${tableStyles.compact.header} pl-6 w-[120px]`}>
          Season
        </th>
        <th className={`${tableStyles.compact.header} w-[250px]`}>
          Competition
        </th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>Tier</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>Pos</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>MP</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>W</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>D</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>L</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>GF</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>GA</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>GD</th>
        <th className={`${tableStyles.compact.header} w-[50px]`}>Pts</th>
        <th className={`${tableStyles.compact.header} w-[100px]`}>
          Attendance
        </th>
        <th className={`${tableStyles.compact.header} w-[350px]`}>Notes</th>
      </tr>
    </thead>
  );
}
