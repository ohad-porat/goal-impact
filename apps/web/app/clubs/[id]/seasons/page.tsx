import { TeamSeasonSquadResponse } from '../../../../lib/types/club'
import { api } from '../../../../lib/api'
import { ErrorDisplay } from '../../../../components/ErrorDisplay'
import { TeamSeasonRosterTableHeader } from './components/TeamSeasonRosterTableHeader'
import { TeamSeasonRosterTableBody } from './components/TeamSeasonRosterTableBody'
import Link from 'next/link'

interface TeamSeasonPageProps {
  params: {
    id: string
  }
  searchParams: {
    season?: string
    from?: string
  }
}

async function getTeamSeasonSquad(teamId: number, seasonId: number): Promise<TeamSeasonSquadResponse> {
  const response = await fetch(api.teamSeasonSquad(teamId, seasonId), {
    cache: 'no-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch team season squad')
  }
  
  return response.json()
}

export default async function TeamSeasonPage({ params, searchParams }: TeamSeasonPageProps) {
  const teamId = parseInt(params.id)
  const seasonId = searchParams.season ? parseInt(searchParams.season) : null
  const from = searchParams.from
  
  if (isNaN(teamId)) {
    return <ErrorDisplay message={`The team ID "${params.id}" is not valid.`} />
  }
  
  if (!seasonId || isNaN(seasonId)) {
    return <ErrorDisplay message="Season parameter is required." />
  }
  
  try {
    const data = await getTeamSeasonSquad(teamId, seasonId)
    const { team, season, competition, players } = data
    
    const breadcrumbs = from === 'league' 
      ? (
          <>
            <Link href="/leagues" className="text-gray-300 hover:text-white transition-colors text-sm">
              Leagues
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/leagues/${data.competition.id}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {competition.name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/leagues/${data.competition.id}?season=${season.id}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {season.display_name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <span className="text-white text-sm">{team.name}</span>
          </>
        )
      : (
          <>
            <Link href="/clubs" className="text-gray-300 hover:text-white transition-colors text-sm">
              Clubs
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <Link href={`/clubs/${team.id}`} className="text-gray-300 hover:text-white transition-colors text-sm">
              {team.name}
            </Link>
            <span className="text-gray-300 mx-2 text-sm">/</span>
            <span className="text-white text-sm">{season.display_name}</span>
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
                {team.name} {season.display_name} ({competition.name})
              </h1>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-8">
          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700 table-fixed">
                <TeamSeasonRosterTableHeader />
                <TeamSeasonRosterTableBody players={players} seasonId={seasonId} teamId={teamId} from={from} />
              </table>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching team season squad:', error)
    return <ErrorDisplay message="The requested team season could not be found or does not exist." />
  }
}
