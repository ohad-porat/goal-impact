import { ClubDetailsResponse } from '../../../lib/types/club'
import { api } from '../../../lib/api'
import { ErrorDisplay } from '../../../components/ErrorDisplay'
import { ClubSeasonsTableHeader } from '../components/ClubSeasonsTableHeader'
import { ClubSeasonsTableBody } from '../components/ClubSeasonsTableBody'

interface ClubShowPageProps {
  params: {
    id: string
  }
}

async function getClubDetails(clubId: number): Promise<ClubDetailsResponse> {
  const response = await fetch(api.clubDetails(clubId), {
    cache: 'force-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch club details')
  }
  
  return response.json()
}

export default async function ClubShowPage({ params }: ClubShowPageProps) {
  const clubId = parseInt(params.id)
  
  if (isNaN(clubId)) {
    return <ErrorDisplay message={`The club ID "${params.id}" is not valid.`} />
  }
  
  try {
    const data = await getClubDetails(clubId)
    const { club, seasons } = data
    
    return (
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <h1 className="text-4xl font-bold text-white">{club.name || 'Unknown Club'}</h1>
            <p className="text-gray-400 text-lg mt-2">
              {club.nation.name || 'Unknown Nation'}
            </p>
          </div>

          <div className="py-8">
            <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <ClubSeasonsTableHeader />
                  <ClubSeasonsTableBody seasons={seasons} teamId={clubId} />
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching club details:', error)
    return <ErrorDisplay message="The requested club could not be found or does not exist." />
  }
}
