'use client'

import { useState, useEffect } from 'react'
import { RecentImpactGoalsResponse } from '../../lib/types/home'
import { League } from '../../lib/types/league'
import { api } from '../../lib/api'
import { getShortLeagueName } from '../../lib/utils'

interface RecentImpactGoalsProps {
  initialLeagues: League[]
}

function formatGoalValue(value: number): string {
  return `+${value.toFixed(2)}`
}

const TOP_LEAGUE_ORDER = ['Premier League', 'Serie A', 'La Liga', 'Bundesliga']

export function RecentImpactGoals({ initialLeagues }: RecentImpactGoalsProps) {
  const [selectedLeagueId, setSelectedLeagueId] = useState<number | undefined>(undefined)
  const [goalsData, setGoalsData] = useState<RecentImpactGoalsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const topLeagues = initialLeagues
    .filter(league => {
      const normalized = getShortLeagueName(league.name)
      return TOP_LEAGUE_ORDER.includes(normalized)
    })
    .sort((a, b) => {
      const nameA = getShortLeagueName(a.name)
      const nameB = getShortLeagueName(b.name)
      const orderA = TOP_LEAGUE_ORDER.indexOf(nameA)
      const orderB = TOP_LEAGUE_ORDER.indexOf(nameB)
      if (orderA === -1 && orderB === -1) return 0
      if (orderA === -1) return 1
      if (orderB === -1) return -1
      return orderA - orderB
    })
    .slice(0, 4)

  useEffect(() => {
    async function fetchGoals() {
      setError(null)
      try {
        const response = await fetch(api.recentGoals(selectedLeagueId), {
          cache: 'no-cache'
        })
        
        if (!response.ok) {
          throw new Error('Failed to fetch recent goals')
        }
        
        const data = await response.json()
        setGoalsData(data)
      } catch (err) {
        setError('Failed to load recent goals.')
        setGoalsData(null)
      }
    }

    fetchGoals()
  }, [selectedLeagueId])

  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-orange-400">Recent Impact Goals</h2>
        
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setSelectedLeagueId(undefined)}
            className={`px-4 py-2 rounded-md font-semibold text-sm transition-colors whitespace-nowrap ${
              selectedLeagueId === undefined
                ? 'bg-orange-400 text-black'
                : 'bg-slate-700 text-white hover:bg-slate-600'
            }`}
          >
            All Leagues
          </button>
          {topLeagues.map((league) => (
            <button
              key={league.id}
              onClick={() => setSelectedLeagueId(league.id)}
              className={`px-4 py-2 rounded-md font-semibold text-sm transition-colors whitespace-nowrap ${
                selectedLeagueId === league.id
                  ? 'bg-orange-400 text-black'
                  : 'bg-slate-700 text-white hover:bg-slate-600'
              }`}
            >
              {getShortLeagueName(league.name)}
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <div className="bg-gray-800 rounded-lg shadow-lg p-8 text-center">
          <p className="text-gray-400 text-lg">{error}</p>
        </div>
      ) : goalsData && goalsData.goals.length === 0 ? (
        <div className="bg-gray-800 rounded-lg shadow-lg p-8 text-center">
          <p className="text-gray-400 text-lg">No recent goals found</p>
        </div>
      ) : goalsData ? (
        <div className="space-y-2">
          {goalsData.goals.map((goal, index) => (
            <div
              key={index}
              className="bg-gray-50 rounded-lg shadow-lg p-4 grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_1fr] gap-4"
            >
              <div className="flex flex-col justify-center">
                <p className="text-gray-900 font-semibold text-base">
                  {goal.match.home_team} vs {goal.match.away_team}
                </p>
                <p className="text-gray-600 text-xs mt-0.5">{goal.match.date}</p>
              </div>

              <div className="flex flex-col justify-center">
                <p className="text-gray-700 text-xs font-semibold mb-0.5">
                  Minute {goal.minute}
                </p>
                <p className="text-gray-900 font-medium text-base">
                  {goal.scorer.name}
                </p>
              </div>

              <div className="flex flex-col justify-center items-end md:items-start">
                <p className="text-gray-700 text-xs font-semibold mb-0.5">Score</p>
                {goal.score_before && goal.score_after ? (
                  <p className="text-gray-700 text-sm">
                    {goal.score_before} → {goal.score_after}
                  </p>
                ) : (
                  <p className="text-gray-400 text-sm">-</p>
                )}
              </div>

              <div className="flex flex-col justify-center items-end md:items-start">
                <p className="text-gray-700 text-xs font-semibold mb-0.5">GV</p>
                <p className="text-gray-900 font-bold text-lg">
                  {formatGoalValue(goal.goal_value)}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  )
}
