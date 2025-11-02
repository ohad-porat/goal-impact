import { PlayerGoalLogResponse } from '../../../../lib/types/club'
import { api } from '../../../../lib/api'
import { ErrorDisplay } from '../../../../components/ErrorDisplay'
import { PlayerGoalLogTableHeader } from './components/PlayerGoalLogTableHeader'
import { PlayerGoalLogTableBody } from './components/PlayerGoalLogTableBody'
import { SeasonSelector } from './components/SeasonSelector'
import { redirect } from 'next/navigation'
import Link from 'next/link'

interface PlayerGoalLogPageProps {
  params: {
    id: string
  }
  searchParams: {
    season?: string
  }
}

async function getPlayerGoalLog(playerId: number): Promise<PlayerGoalLogResponse> {
  const response = await fetch(api.playerGoalLog(playerId), {
    cache: 'no-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch player goal log')
  }
  
  return response.json()
}

function getSeasonStartYear(displayName: string): number {
  const match = displayName.match(/^(\d{4})/)
  return match ? parseInt(match[1], 10) : 0
}

function extractUniqueSeasons(goals: PlayerGoalLogResponse['goals']) {
  const seasonMap = new Map<string, Set<number>>()
  
  goals.forEach((goal) => {
    const { season_display_name: displayName, season_id } = goal
    if (!seasonMap.has(displayName)) {
      seasonMap.set(displayName, new Set())
    }
    seasonMap.get(displayName)!.add(season_id)
  })
  
  return Array.from(seasonMap.entries())
    .map(([displayName, seasonIdSet]) => {
      const seasonIds = Array.from(seasonIdSet)
      return {
        display_name: displayName,
        season_ids: seasonIds,
        id: seasonIds[0]
      }
    })
    .sort((a, b) => {
      const yearA = getSeasonStartYear(a.display_name)
      const yearB = getSeasonStartYear(b.display_name)
      return yearB !== yearA 
        ? yearB - yearA 
        : b.display_name.localeCompare(a.display_name)
    })
}

function isRedirectError(error: unknown): boolean {
  return (
    error !== null &&
    typeof error === 'object' &&
    'digest' in error &&
    typeof error.digest === 'string' &&
    error.digest.startsWith('NEXT_REDIRECT')
  )
}

export default async function PlayerGoalLogPage({ params, searchParams }: PlayerGoalLogPageProps) {
  const playerId = parseInt(params.id)
  
  if (isNaN(playerId)) {
    return <ErrorDisplay message={`The player ID "${params.id}" is not valid.`} />
  }
  
  let data: PlayerGoalLogResponse
  try {
    data = await getPlayerGoalLog(playerId)
  } catch (error) {
    if (isRedirectError(error)) {
      throw error
    }
    console.error('Error fetching player goal log:', error)
    return <ErrorDisplay message="The requested goal log could not be found or does not exist." />
  }

  const { player, goals } = data
  
  const backButton = (
    <Link
      href={`/players/${playerId}`}
      className="px-4 py-2 bg-slate-700 text-white font-semibold rounded-md border border-slate-600 hover:bg-slate-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent whitespace-nowrap flex-shrink-0"
    >
      Back to Player
    </Link>
  )
  
  if (goals.length === 0) {
    return (
      <div className="min-h-screen">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6 flex items-center justify-between gap-4">
            <h1 className="text-4xl font-bold text-white flex-1">
              Goal Log: {player.name}
            </h1>
            {backButton}
          </div>
          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="px-6 py-8 text-center">
              <p className="text-gray-400 text-lg">No goals found for this player</p>
            </div>
          </div>
        </div>
      </div>
    )
  }
  
  const seasons = extractUniqueSeasons(goals)
  const defaultSeason = seasons[0]
  
  if (!searchParams.season && defaultSeason) {
    redirect(`/players/${playerId}/goals?season=${defaultSeason.id}`)
  }
  
  const selectedSeasonId = searchParams.season ? parseInt(searchParams.season) : null
  const selectedSeason = selectedSeasonId 
    ? seasons.find(s => s.season_ids.includes(selectedSeasonId))
    : null
  
  if (!selectedSeason) {
    return <ErrorDisplay message="No valid season found." />
  }
  
  const filteredGoals = goals.filter(goal => selectedSeason.season_ids.includes(goal.season_id))
  
  return (
    <div className="min-h-screen">
      <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h1 className="text-4xl font-bold text-white flex-1">
            Goal Log: {player.name}
          </h1>
          <div className="flex items-center gap-4">
            <SeasonSelector seasons={seasons} selectedSeasonId={selectedSeasonId} />
            {backButton}
          </div>
        </div>

        <div>
          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700 table-fixed">
                <PlayerGoalLogTableHeader />
                <PlayerGoalLogTableBody goals={filteredGoals} />
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
