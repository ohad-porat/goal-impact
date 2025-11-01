'use client'

import { useState, useEffect } from 'react'
import { api } from '../../../lib/api'
import { BySeasonResponse } from '../../../lib/types/leaders'

export function useBySeasonData(seasonId?: number, leagueId?: number) {
  const [data, setData] = useState<BySeasonResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      if (!seasonId) {
        setData(null)
        return
      }

      setLoading(true)
      setError(null)
      try {
        const response = await fetch(api.leadersBySeason(seasonId, leagueId), { cache: 'no-cache' })
        if (!response.ok) {
          throw new Error('Failed to fetch by-season data')
        }
        const responseData: BySeasonResponse = await response.json()
        setData(responseData)
      } catch (err) {
        console.error('Error fetching by-season data:', err)
        setError('Failed to load by-season data.')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [seasonId, leagueId])

  return { data, loading, error }
}
