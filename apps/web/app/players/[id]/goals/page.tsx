import { PlayerGoalLogResponse } from '../../../../lib/types/club'
import { api } from '../../../../lib/api'
import { ErrorDisplay } from '../../../../components/ErrorDisplay'
import { PlayerGoalLogTableHeader } from './components/PlayerGoalLogTableHeader'
import { PlayerGoalLogTableBody } from './components/PlayerGoalLogTableBody'
import Link from 'next/link'

interface PlayerGoalLogPageProps {
  params: {
    id: string
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

export default async function PlayerGoalLogPage({ params }: PlayerGoalLogPageProps) {
  const playerId = parseInt(params.id)
  
  if (isNaN(playerId)) {
    return <ErrorDisplay message={`The player ID "${params.id}" is not valid.`} />
  }
  
  try {
    const data = await getPlayerGoalLog(playerId)
    const { player, goals } = data
    
    return (
      <div className="min-h-screen">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-4xl font-bold text-white">
              Goal Log: {player.name}
            </h1>
            <Link
              href={`/players/${playerId}`}
              className="px-4 py-2 bg-slate-700 text-white font-semibold rounded-md border border-slate-600 hover:bg-slate-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            >
              Back to Player
            </Link>
          </div>

          <div>
            <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700 table-fixed">
                  <PlayerGoalLogTableHeader />
                  <PlayerGoalLogTableBody goals={goals} />
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching player goal log:', error)
    return <ErrorDisplay message="The requested goal log could not be found or does not exist." />
  }
}
