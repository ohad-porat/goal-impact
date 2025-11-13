'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'
import { getShortLeagueName } from '../../../lib/utils'
import { BySeasonTableHeader } from './BySeasonTableHeader'
import { BySeasonTableBody } from './BySeasonTableBody'
import { LeadersTable } from './LeadersTable'
import { useLeagues } from '../hooks/useLeagues'
import { useLeaderFilters } from '../hooks/useLeaderFilters'
import { api } from '../../../lib/api'
import { Season } from '../../../lib/types'
import { BySeasonResponse } from '../../../lib/types/leaders'

function getSeasonsUrl(leagueId?: number): string {
  return leagueId ? api.leagueSeasons(leagueId) : api.allSeasons
}

async function fetchSeasons(leagueId?: number): Promise<Season[]> {
  const response = await fetch(getSeasonsUrl(leagueId), { cache: 'no-cache' })
  if (!response.ok) {
    throw new Error('Failed to fetch seasons')
  }
  const data = await response.json()
  return data.seasons || []
}

async function fetchBySeasonData(seasonId: number, leagueId?: number): Promise<BySeasonResponse> {
  const response = await fetch(api.leadersBySeason(seasonId, leagueId), { cache: 'no-cache' })
  if (!response.ok) {
    throw new Error('Failed to fetch by-season data')
  }
  return response.json()
}

function autoSelectMostRecentSeason(
  seasons: Season[],
  searchParams: URLSearchParams,
  router: ReturnType<typeof useRouter>
) {
  if (seasons.length === 0) return
  
  const mostRecentSeason = seasons[0]
  const params = new URLSearchParams(searchParams.toString())
  params.set('season_id', mostRecentSeason.id.toString())
  if (!params.get('view')) {
    params.set('view', 'season')
  }
  router.push(`/leaders?${params.toString()}`, { scroll: false })
}

export function BySeasonTab() {
  const { leagues, loading: loadingLeagues } = useLeagues()
  const { leagueId, seasonId, selectedLeagueId, selectedSeasonId, updateParams } = useLeaderFilters()
  const searchParams = useSearchParams()
  const router = useRouter()
  const [seasons, setSeasons] = useState<Season[]>([])
  const [loadingSeasons, setLoadingSeasons] = useState(false)
  const [bySeason, setBySeason] = useState<BySeasonResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoadingSeasons(true)
      setBySeason(null)
      setError(null)
      
      try {
        if (seasonId) {
          const [seasonsList, bySeasonData] = await Promise.all([
            fetchSeasons(leagueId),
            fetchBySeasonData(seasonId, leagueId)
          ])
          setSeasons(seasonsList)
          setBySeason(bySeasonData)
        } else {
          const seasonsList = await fetchSeasons(leagueId)
          setSeasons(seasonsList)
          autoSelectMostRecentSeason(seasonsList, searchParams, router)
        }
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load by-season data.')
      } finally {
        setLoadingSeasons(false)
      }
    }
    fetchData()
  }, [leagueId, seasonId, searchParams, router])

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLeagueId = event.target.value === '' ? null : event.target.value
    updateParams('season', { league_id: newLeagueId, season_id: null })
  }

  const handleSeasonChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newSeasonId = event.target.value || null
    updateParams('season', { season_id: newSeasonId })
  }

  const isEmpty = bySeason !== null && bySeason.top_goal_value.length === 0
  const isLoading = loadingSeasons || bySeason === null

  return (
    <div>
      <div className="mb-4 flex items-center justify-between flex-wrap gap-4">
        <h2 className="text-2xl font-bold text-white">Season Leaders by Goal Value</h2>
        <div className="flex gap-4">
          <select
            id="league-filter"
            value={selectedLeagueId || ''}
            onChange={handleLeagueChange}
            className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            disabled={loadingLeagues}
          >
            <option value="">All Leagues</option>
            {leagues.map((league) => (
              <option key={league.id} value={league.id.toString()}>
                {getShortLeagueName(league.name)}
              </option>
            ))}
          </select>
          <select
            id="season-filter"
            value={selectedSeasonId || ''}
            onChange={handleSeasonChange}
            className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            disabled={loadingSeasons || !seasons.length}
          >
            {!seasons.length && <option value="">Loading seasons...</option>}
            {seasons.map((season) => (
              <option key={season.id} value={season.id.toString()}>
                {season.display_name}
              </option>
            ))}
          </select>
        </div>
      </div>
      {isLoading && !error ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-12 h-12 text-orange-400 animate-spin" />
        </div>
      ) : (
        <LeadersTable
          title=""
          header={<BySeasonTableHeader />}
          body={<BySeasonTableBody players={bySeason?.top_goal_value || []} />}
          error={error}
          isEmpty={isEmpty}
        />
      )}
    </div>
  )
}
