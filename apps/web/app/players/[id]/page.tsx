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
    
    const breadcrumbs = from === 'league' && seasonId && teamId
      ? (
          <>
            <Link href="/leagues" className="text-gray-300 hover:text-white transition-colors text-sm">
              Leagues
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/leagues/${seasons[0]?.competition.id}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {seasons[0]?.competition.name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/leagues/${seasons[0]?.competition.id}?season=${seasonId}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {seasons.find((s: any) => s.season.id === seasonId)?.season.display_name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/clubs/${teamId}/seasons?season=${seasonId}&from=league`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {seasons.find((s: any) => s.season.id === seasonId && s.team.id === teamId)?.team.name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <span className="text-white text-sm">{player.name}</span>
          </>
        )
      : from === 'team' && seasonId && teamId
      ? (
          <>
            <Link href="/clubs" className="text-gray-300 hover:text-white transition-colors text-sm">
              Clubs
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/clubs/${teamId}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {seasons.find((s: any) => s.season.id === seasonId && s.team.id === teamId)?.team.name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/clubs/${teamId}/seasons?season=${seasonId}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {seasons.find((s: any) => s.season.id === seasonId)?.season.display_name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <span className="text-white text-sm">{player.name}</span>
          </>
        )
      : (
          <>
            <span className="text-white text-sm">{player.name}</span>
          </>
        )
    
    return (
      <div className="min-h-screen">
        <div className="px-6 py-4">
          <div className="max-w-7xl mx-auto">
            {breadcrumbs}
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center">
              <h1 className="text-4xl font-bold text-white ml-4">
                {player.name}
              </h1>
            </div>
            {player.nation?.name && (
              <div className="ml-4 mt-2">
                <p className="text-xl text-gray-300">
                  Country: {player.nation.name}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-8">
          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700">
                <PlayerTableHeader />
                <PlayerTableBody seasons={seasons} />
              </table>
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
