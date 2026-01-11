'use client'

import { useState, useEffect } from 'react'
import { Loader2 } from 'lucide-react'
import { getShortLeagueName } from '../../../lib/utils'
import { AllSeasonsTableHeader } from './AllSeasonsTableHeader'
import { AllSeasonsTableBody } from './AllSeasonsTableBody'
import { LeadersTable } from './LeadersTable'
import { useLeagues } from '../hooks/useLeagues'
import { useLeaderFilters } from '../hooks/useLeaderFilters'
import { api } from '../../../lib/api'
import { AllSeasonsResponse } from '../../../lib/types/leaders'

async function fetchAllSeasonsData(leagueId?: number): Promise<AllSeasonsResponse> {
  const response = await fetch(api.leadersAllSeasons(leagueId), { cache: 'no-cache' })
  if (!response.ok) {
    throw new Error('Failed to fetch all-seasons data')
  }
  return response.json()
}

export function AllSeasonsTab() {
  const { leagues, loading: loadingLeagues } = useLeagues()
  const { leagueId, selectedLeagueId, updateParams } = useLeaderFilters()
  const [allSeasons, setAllSeasons] = useState<AllSeasonsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setAllSeasons(null)
      setError(null)

      try {
        const data = await fetchAllSeasonsData(leagueId)
        setAllSeasons(data)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load all-seasons data.')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [leagueId])

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLeagueId = event.target.value === '' ? null : event.target.value
    updateParams('all-seasons', { league_id: newLeagueId })
  }

  const isEmpty = allSeasons !== null && allSeasons.top_goal_value.length === 0
  const isLoading = loading || allSeasons === null

  return (
    <div>
      <div className="mb-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 className="text-xl sm:text-2xl font-bold text-white">All Seasons Leaders by Goal Value</h2>
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          <select
            id="league-filter"
            value={selectedLeagueId || ''}
            onChange={handleLeagueChange}
            className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent w-full sm:w-auto"
            disabled={loadingLeagues}
          >
            <option value="">All Leagues</option>
            {leagues.map((league) => (
              <option key={league.id} value={league.id.toString()}>
                {getShortLeagueName(league.name)}
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
          header={<AllSeasonsTableHeader />}
          body={<AllSeasonsTableBody players={allSeasons?.top_goal_value || []} />}
          error={error}
          isEmpty={isEmpty}
        />
      )}
    </div>
  )
}
