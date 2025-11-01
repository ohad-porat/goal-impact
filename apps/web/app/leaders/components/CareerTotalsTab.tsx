'use client'

import { useState, useEffect } from 'react'
import { api } from '../../../lib/api'
import { CareerTotalsResponse } from '../../../lib/types/leaders'
import { getShortLeagueName } from '../../../lib/utils'
import { CareerTotalsTableHeader } from './CareerTotalsTableHeader'
import { CareerTotalsTableBody } from './CareerTotalsTableBody'
import { LeadersTable } from './LeadersTable'
import { useLeagues } from '../hooks/useLeagues'
import { useLeaderFilters } from '../hooks/useLeaderFilters'

export function CareerTotalsTab() {
  const { leagues, loading: loadingLeagues } = useLeagues()
  const { leagueId, selectedLeagueId, updateParams } = useLeaderFilters()
  const [careerTotals, setCareerTotals] = useState<CareerTotalsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCareerTotals = async () => {
      setCareerTotals(null)
      setError(null)
      try {
        const response = await fetch(api.leadersCareerTotals(leagueId), { cache: 'no-cache' })
        if (!response.ok) {
          throw new Error('Failed to fetch career totals')
        }
        const data: CareerTotalsResponse = await response.json()
        setCareerTotals(data)
      } catch (err) {
        console.error('Error fetching career totals:', err)
        setError('Failed to load career totals data.')
      }
    }
    fetchCareerTotals()
  }, [leagueId])

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLeagueId = event.target.value === '' ? null : event.target.value
    updateParams('career', { league_id: newLeagueId })
  }

  const isEmpty = careerTotals !== null && careerTotals.top_goal_value.length === 0

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Career Leaders by Goal Value</h2>
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
      </div>
      {careerTotals !== null || error ? (
        <LeadersTable
          title=""
          header={<CareerTotalsTableHeader />}
          body={<CareerTotalsTableBody players={careerTotals?.top_goal_value || []} />}
          error={error}
          isEmpty={isEmpty}
        />
      ) : null}
    </div>
  )
}
