'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { api } from '../../../lib/api'
import { CareerTotalsResponse } from '../../../lib/types/leaders'
import { League } from '../../../lib/types'
import { getShortLeagueName } from '../../../lib/utils'
import { CareerTotalsTableHeader } from './CareerTotalsTableHeader'
import { CareerTotalsTableBody } from './CareerTotalsTableBody'
import { LeadersTable } from './LeadersTable'

export function CareerTotalsTab() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [careerTotals, setCareerTotals] = useState<CareerTotalsResponse | null>(null)
  const [leagues, setLeagues] = useState<League[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingLeagues, setLoadingLeagues] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const selectedLeagueId = searchParams.get('league_id')
  const leagueId = selectedLeagueId && !isNaN(parseInt(selectedLeagueId, 10)) 
    ? parseInt(selectedLeagueId, 10) 
    : undefined

  useEffect(() => {
    const fetchLeagues = async () => {
      setLoadingLeagues(true)
      try {
        const response = await fetch(api.leagues, { cache: 'force-cache' })
        if (!response.ok) {
          throw new Error('Failed to fetch leagues')
        }
        const data = await response.json()
        setLeagues(data.leagues || [])
      } catch (err) {
        console.error('Error fetching leagues:', err)
      } finally {
        setLoadingLeagues(false)
      }
    }
    fetchLeagues()
  }, [])

  useEffect(() => {
    const fetchCareerTotals = async () => {
      setLoading(true)
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
      } finally {
        setLoading(false)
      }
    }
    fetchCareerTotals()
  }, [leagueId])

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLeagueId = event.target.value === '' ? null : event.target.value
    const params = new URLSearchParams(searchParams.toString())
    
    if (!params.get('view')) {
      params.set('view', 'career')
    }
    
    if (newLeagueId) {
      params.set('league_id', newLeagueId)
    } else {
      params.delete('league_id')
    }
    router.push(`/leaders?${params.toString()}`, { scroll: false })
  }

  const isEmpty = !careerTotals || careerTotals.top_goal_value.length === 0

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
      <LeadersTable
        title=""
        header={<CareerTotalsTableHeader />}
        body={<CareerTotalsTableBody players={careerTotals?.top_goal_value || []} />}
        loading={loading}
        error={error}
        isEmpty={isEmpty}
      />
    </div>
  )
}
