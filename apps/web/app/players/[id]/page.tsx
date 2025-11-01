import { PlayerDetailsResponse } from '../../../lib/types/player'
import { api } from '../../../lib/api'
import { ErrorDisplay } from '../../../components/ErrorDisplay'
import { PlayerTableHeader } from './components/PlayerTableHeader'
import { PlayerTableBody } from './components/PlayerTableBody'

interface PlayerPageProps {
  params: {
    id: string
  }
  searchParams: {
    from?: string
    season?: string
    teamId?: string
  }
}

async function getPlayerDetails(playerId: number): Promise<PlayerDetailsResponse> {
  const response = await fetch(api.playerDetails(playerId), {
    cache: 'no-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch player details')
  }
  
  return response.json()
}

export default async function PlayerPage({ params, searchParams }: PlayerPageProps) {
  const playerId = parseInt(params.id)
  const from = searchParams.from
  const seasonId = searchParams.season ? parseInt(searchParams.season) : null
  const teamId = searchParams.teamId ? parseInt(searchParams.teamId) : null
  
  if (isNaN(playerId)) {
    return <ErrorDisplay message={`The player ID "${params.id}" is not valid.`} />
  }
  
  try {
    const data = await getPlayerDetails(playerId)
    const { player, seasons } = data
    
    return (
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <h1 className="text-4xl font-bold text-white">
              {player.name}
            </h1>
            {player.nation?.name && (
              <div className="mt-2">
                <p className="text-xl text-gray-300">
                  Country: {player.nation.name}
                </p>
              </div>
            )}
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
