import { TeamSeasonGoalLogResponse } from '../../../../../lib/types/club'
import { api } from '../../../../../lib/api'
import { ErrorDisplay } from '../../../../../components/ErrorDisplay'
import { TeamSeasonGoalLogTableHeader } from './components/TeamSeasonGoalLogTableHeader'
import { TeamSeasonGoalLogTableBody } from './components/TeamSeasonGoalLogTableBody'
import Link from 'next/link'

interface GoalLogPageProps {
  params: {
    id: string
  }
  searchParams: {
    season?: string
  }
}

async function getTeamSeasonGoalLog(teamId: number, seasonId: number): Promise<TeamSeasonGoalLogResponse> {
  const response = await fetch(api.teamSeasonGoalLog(teamId, seasonId), {
    cache: 'no-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch team season goal log')
  }
  
  return response.json()
}

export default async function GoalLogPage({ params, searchParams }: GoalLogPageProps) {
  const teamId = parseInt(params.id)
  const seasonId = searchParams.season ? parseInt(searchParams.season) : null
  
  if (isNaN(teamId)) {
    return <ErrorDisplay message={`The team ID "${params.id}" is not valid.`} />
  }
  
  if (!seasonId || isNaN(seasonId)) {
    return <ErrorDisplay message="Season parameter is required." />
  }
  
  try {
    const data = await getTeamSeasonGoalLog(teamId, seasonId)
    const { team, season, competition, goals } = data
    
    return (
      <div className="min-h-screen">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-4xl font-bold text-white">
              Goal Log: {team.name} {season.display_name} ({competition.name})
            </h1>
            <Link
              href={`/clubs/${teamId}/seasons?season=${seasonId}`}
              className="px-4 py-2 bg-slate-700 text-white font-semibold rounded-md border border-slate-600 hover:bg-slate-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            >
              Back to Roster
            </Link>
          </div>

          <div>
            <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700 table-fixed">
                  <TeamSeasonGoalLogTableHeader />
                  <TeamSeasonGoalLogTableBody goals={goals} />
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching team season goal log:', error)
    return <ErrorDisplay message="The requested goal log could not be found or does not exist." />
  }
}
