'use client'

import { useState, useEffect } from 'react'
import { Loader2 } from 'lucide-react'
import { api } from '../../../lib/api'
import { CareerTotalsResponse } from '../../../lib/types/leaders'
import { League } from '../../../lib/types'
import { getShortLeagueName } from '../../../lib/utils'
import { CareerTotalsTableHeader } from './CareerTotalsTableHeader'
import { CareerTotalsTableBody } from './CareerTotalsTableBody'
import { LeadersTable } from './LeadersTable'
import { useLeaderFilters } from '../hooks/useLeaderFilters'

export function CareerTotalsTab() {
  const { leagueId, selectedLeagueId, updateParams } = useLeaderFilters()
  const [leagues, setLeagues] = useState<League[]>([])
  const [loadingLeagues, setLoadingLeagues] = useState(false)
  const [careerTotals, setCareerTotals] = useState<CareerTotalsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setCareerTotals(null)
      setError(null)
      setLoadingLeagues(true)
      
      try {
        const [leaguesResponse, careerResponse] = await Promise.all([
          fetch(api.leagues, { cache: 'no-cache' }),
          fetch(api.leadersCareerTotals(leagueId), { cache: 'no-cache' })
        ])
        
        if (!leaguesResponse.ok) {
          throw new Error('Failed to fetch leagues')
        }
        if (!careerResponse.ok) {
          throw new Error('Failed to fetch career totals')
        }
        
        const leaguesData = await leaguesResponse.json()
        const careerData = await careerResponse.json()
        
        setLeagues(leaguesData.leagues || [])
        setCareerTotals(careerData)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load career totals data.')
      } finally {
        setLoadingLeagues(false)
      }
    }
    fetchData()
  }, [leagueId])

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLeagueId = event.target.value === '' ? null : event.target.value
    updateParams('career', { league_id: newLeagueId })
  }

  const isEmpty = careerTotals !== null && careerTotals.top_goal_value.length === 0
  const isLoading = loadingLeagues || careerTotals === null

  return (
    <div>
      <div className="mb-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h2 className="text-xl sm:text-2xl font-bold text-white">Career Leaders by Goal Value</h2>
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
      {isLoading && !error ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-12 h-12 text-orange-400 animate-spin" />
        </div>
      ) : (
        <LeadersTable
          title=""
          header={<CareerTotalsTableHeader />}
          body={<CareerTotalsTableBody players={careerTotals?.top_goal_value || []} />}
          error={error}
          isEmpty={isEmpty}
        />
      )}
    </div>
  )
}
