'use client'

import { useState, useEffect } from 'react'
import { api } from '../../../lib/api'
import { League } from '../../../lib/types'

export function useLeagues() {
  const [leagues, setLeagues] = useState<League[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchLeagues = async () => {
      setLoading(true)
      try {
        const response = await fetch(api.leagues, { cache: 'no-cache' })
        if (!response.ok) {
          throw new Error('Failed to fetch leagues')
        }
        const data = await response.json()
        setLeagues(data.leagues || [])
      } catch (err) {
        console.error('Error fetching leagues:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchLeagues()
  }, [])

  return { leagues, loading }
}
