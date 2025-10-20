'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { LeagueTableData, Season } from '../../../lib/types'
import { api } from '../../../lib/api'
import { tableStyles, leagueTableColumns } from '../../../lib/tableStyles'

interface LeagueShowClientProps {
  initialData: LeagueTableData
  seasons: Season[]
  leagueId: number
}

export default function LeagueShowClient({ initialData, seasons, leagueId }: LeagueShowClientProps) {
  const [tableData, setTableData] = useState<LeagueTableData>(initialData)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSeasonChange = async (seasonId: number) => {
    setLoading(true)
    try {
      const response = await fetch(api.leagueTable(leagueId, seasonId))
      if (response.ok) {
        const newData = await response.json()
        setTableData(newData)
        router.replace(`/leagues/${leagueId}/${seasonId}`, { scroll: false })
      }
    } catch (error) {
      console.error('Error fetching table data:', error)
    } finally {
      setLoading(false)
    }
  }

  const styles = tableStyles.compact

  const renderTableCell = (team: any, column: any) => {
    const value = team[column.key]
    
    if (column.key === 'team_name') {
      return (
        <td className={styles.cell}>
          <div className={styles.text.teamName}>
            {value}
          </div>
        </td>
      )
    }
    
    if (column.key === 'points') {
      return (
        <td className={styles.cell}>
          <div className={styles.text.points}>
            {value}
          </div>
        </td>
      )
    }
    
    return (
      <td className={styles.cell}>
        <div className={column.align === 'left' ? styles.text.primary : styles.text.center}>
          {value}
        </div>
      </td>
    )
  }

  return (
    <div className="min-h-screen">
      <div className="px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <Link href="/leagues" className="text-gray-300 hover:text-white transition-colors text-sm">
            Competitions
          </Link>
          <span className="text-gray-300 mx-2 text-sm">/</span>
          <span className="text-white text-sm">{tableData.league.name}</span>
        </div>
      </div>

      <div className="px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center">
            <h1 className="text-4xl font-bold text-white ml-4">{tableData.league.name}</h1>
            <select
              value={tableData.season.id}
              onChange={(e) => handleSeasonChange(parseInt(e.target.value))}
              disabled={loading}
              className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-orange-500 focus:outline-none ml-6"
            >
              {seasons.map((season) => (
                <option key={season.id} value={season.id}>
                  {season.display_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-orange-400">
                <tr>
                  {leagueTableColumns.map((column) => (
                    <th 
                      key={column.key}
                      className={column.align === 'left' ? styles.headerLeft : styles.header}
                    >
                      {column.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-slate-800 divide-y divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan={leagueTableColumns.length} className={styles.text.center}>
                      Loading...
                    </td>
                  </tr>
                ) : tableData.table.length === 0 ? (
                  <tr>
                    <td colSpan={leagueTableColumns.length} className={styles.text.center}>
                      No data available
                    </td>
                  </tr>
                ) : (
                  tableData.table.map((team, index) => (
                    <tr key={team.position} className={`${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'} hover:bg-slate-700 transition-colors`}>
                      {leagueTableColumns.map((column) => (
                        <React.Fragment key={column.key}>
                          {renderTableCell(team, column)}
                        </React.Fragment>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
