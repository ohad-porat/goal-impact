import { PlayerDetailsResponse } from '../../../lib/types/player'
import { api } from '../../../lib/api'
import { ErrorDisplay } from '../../../components/ErrorDisplay'
import { PlayerTableHeader } from './components/PlayerTableHeader'
import { PlayerTableBody } from './components/PlayerTableBody'
import Link from 'next/link'

interface PlayerPageProps {
  params: {
    id: string
  }
}

async function getPlayerDetails(playerId: number): Promise<PlayerDetailsResponse> {
  const response = await fetch(api.playerDetails(playerId), {
    next: { revalidate: 86400 }
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch player details')
  }
  
  return response.json()
}

export default async function PlayerPage({ params }: PlayerPageProps) {
  const playerId = parseInt(params.id)
  
  if (isNaN(playerId)) {
    return <ErrorDisplay message={`The player ID "${params.id}" is not valid.`} />
  }
  
  try {
    const data = await getPlayerDetails(playerId)
    const { player, seasons } = data
    
    return (
      <div className="min-h-screen">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white">
                {player.name}
              </h1>
              {player.nation?.name && (
                <div className="mt-2">
                  <p className="text-lg sm:text-xl text-gray-300">
                    Country: {player.nation.name}
                  </p>
                </div>
              )}
            </div>
            <Link
              href={`/players/${playerId}/goals`}
              className="px-4 py-2 bg-slate-700 text-white font-semibold rounded-md border border-slate-600 hover:bg-slate-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent whitespace-nowrap flex-shrink-0"
            >
              View Goal Log
            </Link>
          </div>

          <div>
            <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700 table-fixed">
                  <PlayerTableHeader />
                  <PlayerTableBody seasons={seasons} />
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching player details:', error)
    return <ErrorDisplay message="The requested player could not be found or does not exist." />
  }
}
