'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { LeagueTableData, Season } from '../../../lib/types'
import { api } from '../../../lib/api'
import { LeagueTableHeader } from '../components/LeagueTableHeader'
import { LeagueTableBody } from '../components/LeagueTableBody'
import { ErrorDisplay } from '../../../components/ErrorDisplay'

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
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  React.useEffect(() => {
    if (isNaN(leagueId)) {
      setError(`The league ID "${params.id}" is not valid.`)
      return
    }

    const loadInitialData = async () => {
      try {
        const seasonsData = await getLeagueSeasons(leagueId)
        
        if (seasonsData.length === 0) {
          setError("The requested league has no available seasons.")
          return
        }

        setSeasons(seasonsData)
        const targetSeasonId = getTargetSeasonId(seasonId, seasonsData)
        const leagueTableData = await getLeagueTable(leagueId, targetSeasonId)
        setTableData(leagueTableData)
      } catch (error) {
        console.error('Error fetching league data:', error)
        if (error instanceof Error && error.message === 'Invalid season') {
          setError("The requested season is not valid.")
        } else {
          setError("The requested league could not be found or does not exist.")
        }
      }
    }

    loadInitialData()
  }, [leagueId, seasonId, params.id])

  const handleSeasonChange = async (newSeasonId: number) => {
    try {
      setError(null)
      const newData = await getLeagueTable(leagueId, newSeasonId)
      setTableData(newData)
      router.replace(`/leagues/${leagueId}?season=${newSeasonId}`, { scroll: false })
    } catch (error) {
      console.error('Error fetching table data:', error)
      setError("Failed to load league table data for the selected season.")
    }
  }

  if (error) {
    return <ErrorDisplay message={error} />
  }

  if (!tableData) {
    return null
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <div className="flex items-center">
            <h1 className="text-4xl font-bold text-white">{tableData.league.name}</h1>
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

        <div className="py-8">
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
    </div>
  )
}
