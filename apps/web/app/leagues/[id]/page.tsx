import { LeagueTableData, Season } from '../../../lib/types'
import { api } from '../../../lib/api'
import { LeagueTableHeader } from '../components/LeagueTableHeader'
import { LeagueTableBody } from '../components/LeagueTableBody'
import { ErrorDisplay } from '../../../components/ErrorDisplay'
import { SeasonSelector } from './components/SeasonSelector'

async function getLeagueSeasons(leagueId: number): Promise<Season[]> {
  const cacheOption = process.env.DISABLE_FETCH_CACHE === 'true' ? 'no-store' : 'default'
  const nextOption = process.env.DISABLE_FETCH_CACHE === 'true' ? undefined : { revalidate: 86400 }
  
  const response = await fetch(api.leagueSeasons(leagueId), {
    cache: cacheOption,
    next: nextOption
  })
  if (!response.ok) {
    throw new Error('Failed to fetch league seasons')
  }
  const data = await response.json()
  return data.seasons
}

async function getLeagueTable(leagueId: number, seasonId: number): Promise<LeagueTableData> {
  const response = await fetch(api.leagueTable(leagueId, seasonId), {
    next: { revalidate: 86400 }
  })
  if (!response.ok) {
    throw new Error('Failed to fetch league table')
  }
  return response.json()
}

const getTargetSeasonId = (seasonId: number | null, seasons: Season[]): number => {
  if (seasonId && !isNaN(seasonId)) {
    const requestedSeason = seasons.find(season => season.id === seasonId)
    if (!requestedSeason) {
      throw new Error('Invalid season')
    }
    return seasonId
  }
  return seasons[0].id
}

interface LeagueShowPageProps {
  params: {
    id: string
  }
  searchParams: {
    season?: string
  }
}

export default async function LeagueShowPage({ params, searchParams }: LeagueShowPageProps) {
  const leagueId = parseInt(params.id)
  const seasonId = searchParams.season ? parseInt(searchParams.season) : null

  if (isNaN(leagueId)) {
    return <ErrorDisplay message={`The league ID "${params.id}" is not valid.`} />
  }

  try {
    const seasons = await getLeagueSeasons(leagueId)

    if (seasons.length === 0) {
      return <ErrorDisplay message="The requested league has no available seasons." />
    }

    const targetSeasonId = getTargetSeasonId(seasonId, seasons)
    const tableData = await getLeagueTable(leagueId, targetSeasonId)

    return (
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white">{tableData.league.name}</h1>
              <div className="w-full sm:w-auto">
                <SeasonSelector 
                  seasons={seasons} 
                  currentSeasonId={targetSeasonId}
                  leagueId={leagueId}
                />
              </div>
            </div>
          </div>

          <div>
            <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700 table-fixed">
                  <LeagueTableHeader />
                  <LeagueTableBody tableData={tableData} />
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching league data:', error)
    if (error instanceof Error && error.message === 'Invalid season') {
      return <ErrorDisplay message="The requested season is not valid." />
    }
    return <ErrorDisplay message="The requested league could not be found or does not exist." />
  }
}
