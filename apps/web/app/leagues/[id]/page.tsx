'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { LeagueTableData, Season } from '../../../lib/types'
import { api } from '../../../lib/api'
import { LeagueTableHeader } from '../components/LeagueTableHeader'
import { LeagueTableBody } from '../components/LeagueTableBody'

const fetchWithErrorHandling = async (url: string) => {
  const response = await fetch(url, { cache: 'no-cache' })
  if (!response.ok) {
    throw new Error(`Failed to fetch data from ${url}`)
  }
  return response.json()
}

const getTargetSeasonId = (seasonId: number | null, seasons: Season[]): number => {
  if (seasonId && !isNaN(seasonId)) {
    const requestedSeason = seasons.find(s => s.id === seasonId)
    if (!requestedSeason) {
      throw new Error('Invalid season')
    }
    return seasonId
  }
  return seasons[0].id
}

async function getLeagueSeasons(leagueId: number): Promise<Season[]> {
  const data = await fetchWithErrorHandling(api.leagueSeasons(leagueId))
  return data.seasons
}

async function getLeagueTable(leagueId: number, seasonId: number): Promise<LeagueTableData> {
  return await fetchWithErrorHandling(api.leagueTable(leagueId, seasonId))
}

interface LeagueShowPageProps {
  params: {
    id: string
  }
  searchParams: {
    season?: string
  }
}

export default function LeagueShowPage({ params, searchParams }: LeagueShowPageProps) {
  const leagueId = parseInt(params.id)
  const seasonId = searchParams.season ? parseInt(searchParams.season) : null
  const [tableData, setTableData] = useState<LeagueTableData | null>(null)
  const [seasons, setSeasons] = useState<Season[]>([])
  const router = useRouter()

  React.useEffect(() => {
    if (isNaN(leagueId)) {
      router.push('/leagues')
      return
    }

    const loadInitialData = async () => {
      try {
        const seasonsData = await getLeagueSeasons(leagueId)
        
        if (seasonsData.length === 0) {
          router.push('/leagues')
          return
        }

        setSeasons(seasonsData)
        const targetSeasonId = getTargetSeasonId(seasonId, seasonsData)
        const leagueTableData = await getLeagueTable(leagueId, targetSeasonId)
        setTableData(leagueTableData)
      } catch (error) {
        console.error('Error fetching league data:', error)
        if (error instanceof Error && error.message === 'Invalid season') {
          router.replace(`/leagues/${leagueId}`)
        } else {
          router.push('/leagues')
        }
      }
    }

    loadInitialData()
  }, [leagueId, seasonId, router])

  const handleSeasonChange = async (newSeasonId: number) => {
    try {
      const newData = await getLeagueTable(leagueId, newSeasonId)
      setTableData(newData)
      router.replace(`/leagues/${leagueId}?season=${newSeasonId}`, { scroll: false })
    } catch (error) {
      console.error('Error fetching table data:', error)
    }
  }

  if (!tableData) {
    return null
  }

  return (
    <div className="min-h-screen">
      <div className="px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <Link href="/leagues" className="text-gray-300 hover:text-white transition-colors text-sm">
            Leagues
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
            <table className="min-w-full divide-y divide-gray-700 table-fixed">
              <LeagueTableHeader />
              <LeagueTableBody tableData={tableData} />
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
