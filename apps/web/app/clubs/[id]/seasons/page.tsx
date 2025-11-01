import { TeamSeasonSquadResponse } from '../../../../lib/types/club'
import { api } from '../../../../lib/api'
import { ErrorDisplay } from '../../../../components/ErrorDisplay'
import { TeamSeasonRosterTableHeader } from './components/TeamSeasonRosterTableHeader'
import { TeamSeasonRosterTableBody } from './components/TeamSeasonRosterTableBody'

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
    
    return (
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <h1 className="text-4xl font-bold text-white">
              {team.name} {season.display_name} ({competition.name})
            </h1>
          </div>

          <div>
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
      </div>
    )
  } catch (error) {
    console.error('Error fetching team season squad:', error)
    return <ErrorDisplay message="The requested team season could not be found or does not exist." />
  }
}
