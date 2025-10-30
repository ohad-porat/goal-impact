import { api } from '../../../lib/api'
import { NationDetailsResponse } from '../../../lib/types/nation'
import Link from 'next/link'
import { ErrorDisplay } from '../../../components/ErrorDisplay'
import { NationCompetitionsList } from './components/NationCompetitionsList'
import { NationClubsTable } from './components/NationClubsTable'
import { NationPlayersTable } from './components/NationPlayersTable'

interface NationShowPageProps {
  params: { id: string }
}

async function getNationDetails(nationId: number): Promise<NationDetailsResponse> {
  const response = await fetch(api.nationDetails(nationId), {
    cache: 'force-cache'
  })
  if (!response.ok) {
    throw new Error('Failed to fetch nation details')
  }
  return response.json()
}

export default async function NationShowPage({ params }: NationShowPageProps) {
  const nationId = parseInt(params.id)
  if (isNaN(nationId)) {
    return <ErrorDisplay message={`The nation ID "${params.id}" is not valid.`} />
  }

  try {
    const data = await getNationDetails(nationId)
    const { nation, competitions, clubs, players } = data

    return (
      <div className="min-h-screen py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <Link href="/nations" className="hover:text-white transition-colors">Nations</Link>
              <span>/</span>
              <span className="text-white">{nation.name}</span>
            </div>
            <h1 className="text-4xl font-bold text-white mt-2">{nation.name}</h1>
            <p className="text-gray-400 mt-1">FIFA Code: {nation.country_code} • Governing Body: {nation.governing_body}</p>
          </div>

          <NationCompetitionsList competitions={competitions} />
          <NationClubsTable clubs={clubs} />
          <NationPlayersTable players={players} />
        </div>
      </div>
    )
  } catch (error) {
    console.error('Error fetching nation details:', error)
    return <ErrorDisplay message="The requested nation could not be found or does not exist." />
  }
}
