'use client'

import { useState, useEffect } from 'react'
import { api } from '../../../lib/api'
import { CareerTotalsResponse } from '../../../lib/types/leaders'
import { CareerTotalsTableHeader } from './CareerTotalsTableHeader'
import { CareerTotalsTableBody } from './CareerTotalsTableBody'
import { ErrorDisplay } from '../../../components/ErrorDisplay'

export function CareerTotalsTab() {
  const [careerTotals, setCareerTotals] = useState<CareerTotalsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCareerTotals = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(api.leadersCareerTotals(), { cache: 'no-cache' })
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
  }, [])

  if (error) {
    return <ErrorDisplay message={error} />
  }

  if (loading) {
    return (
      <div className="text-white text-center py-8">
        <p>Loading career totals...</p>
      </div>
    )
  }

  if (!careerTotals || careerTotals.top_goal_value.length === 0) {
    return (
      <div className="text-white text-center">
        <p>No data available</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-4">Career Leaders by Goal Value</h2>
      <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <CareerTotalsTableHeader />
              <CareerTotalsTableBody 
                players={careerTotals.top_goal_value} 
              />
          </table>
        </div>
      </div>
    </div>
  )
}
