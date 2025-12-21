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
    next: { revalidate: 86400 }
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch club details')
  }
  
  return response.json()
}

const ClubDetailsContent = ({ club, seasons, clubId }: { 
  club: ClubDetailsResponse['club']
  seasons: ClubDetailsResponse['seasons']
  clubId: number 
}) => {
  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white">{club.name || 'Unknown Club'}</h1>
          <p className="text-gray-400 text-base sm:text-lg mt-2">
            {club.nation.name || 'Unknown Nation'}
          </p>
        </div>

        <div>
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
}

export default async function ClubShowPage({ params }: ClubShowPageProps) {
  const { id } = await params
  const clubId = parseInt(id)
  
  if (isNaN(clubId)) {
    return <ErrorDisplay message={`The club ID "${id}" is not valid.`} />
  }
  
  let club: ClubDetailsResponse['club']
  let seasons: ClubDetailsResponse['seasons']
  
  try {
    const data = await getClubDetails(clubId)
    club = data.club
    seasons = data.seasons
  } catch (error) {
    console.error('Error fetching club details:', error)
    return <ErrorDisplay message="The requested club could not be found or does not exist." />
  }
  
  return <ClubDetailsContent club={club} seasons={seasons} clubId={clubId} />
}
