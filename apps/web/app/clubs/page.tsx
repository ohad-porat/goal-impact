import { ClubsResponse } from '../../lib/types/club'
import { api } from '../../lib/api'
import Link from 'next/link'

async function getClubsByNation(): Promise<ClubsResponse> {
  const response = await fetch(api.clubs, {
    cache: 'force-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch clubs')
  }
  
  return response.json()
}

export default async function ClubsPage() {
  const data = await getClubsByNation()
  
  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Top Clubs</h1>
        </div>

        {data.nations.length === 0 ? (
          <div className="bg-gray-800 rounded-lg shadow-lg p-8 text-center">
            <p className="text-gray-400 text-lg">No clubs data available</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {data.nations.map((nationData) => (
              <div key={nationData.nation.id} className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <div className="bg-gray-700 px-4 py-3 border-b border-gray-600 text-center">
                  <h2 className="text-xl font-semibold text-white">
                    {nationData.nation.name}
                  </h2>
                </div>
                <div className="p-4">
                  {nationData.clubs.length === 0 ? (
                    <p className="text-gray-400 text-sm">No clubs with 1st place finishes</p>
                  ) : (
                    <div className="space-y-1">
                      {nationData.clubs.map((club) => (
                        <Link 
                          key={club.id} 
                          href={`/clubs/${club.id}`}
                          className="block px-4 py-2 hover:bg-slate-700 transition-colors -mx-4"
                        >
                          <p className="text-white font-medium text-sm">
                            {club.name}
                          </p>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
