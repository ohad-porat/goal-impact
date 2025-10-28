import React from 'react'
import { tableStyles } from '../../../../../lib/tableStyles'

export function TeamSeasonRosterTableHeader() {
  const { teamSeason } = tableStyles
  
  return (
    <thead className="bg-gray-700">
      <tr>
        <th rowSpan={2} className={`${teamSeason.headerLeft} pl-3 w-[380px]`}>
          Player
        </th>
        <th colSpan={2} className={`${teamSeason.headerBottom}`}>
          Goal Value
        </th>
        <th colSpan={8} className={`${teamSeason.headerBottom}`}>
          Performance
        </th>
        <th colSpan={5} className={`${teamSeason.headerBottom}`}>
          Per 90 Minutes
        </th>
        <th colSpan={4} className={`${teamSeason.header} border-b border-gray-600`}>
          Playing Time
        </th>
      </tr>
      
      <tr>
        <th className={`${teamSeason.header} w-[85px]`}>Total</th>
        <th className={`${teamSeason.header} w-[85px]`}>Avg</th>
        
        <th className={`${teamSeason.header} w-[85px]`}>Gls</th>
        <th className={`${teamSeason.header} w-[85px]`}>Ast</th>
        <th className={`${teamSeason.header} w-[85px]`}>G+A</th>
        <th className={`${teamSeason.header} w-[85px]`}>G-PK</th>
        <th className={`${teamSeason.header} w-[85px]`}>PK</th>
        <th className={`${teamSeason.header} w-[85px]`}>PK att</th>
        <th className={`${teamSeason.header} w-[85px]`}>Yellow</th>
        <th className={`${teamSeason.header} w-[85px]`}>Red</th>
        
        <th className={`${teamSeason.header} w-[85px]`}>Gls</th>
        <th className={`${teamSeason.header} w-[85px]`}>Ast</th>
        <th className={`${teamSeason.header} w-[85px]`}>G+A</th>
        <th className={`${teamSeason.header} w-[85px]`}>G-PK</th>
        <th className={`${teamSeason.header} w-[90px]`}>G+A-PK</th>
        
        <th className={`${teamSeason.header} w-[85px]`}>MP</th>
        <th className={`${teamSeason.header} w-[85px]`}>Starts</th>
        <th className={`${teamSeason.header} w-[85px]`}>Min</th>
        <th className={`${teamSeason.header} border-r-0 w-[85px]`}>90s</th>
      </tr>
    </thead>
  )
}
