import Link from 'next/link'
import { NationCompetition } from '../../../../lib/types/nation'

interface NationCompetitionsListProps {
  competitions: NationCompetition[]
}

export function NationCompetitionsList({ competitions }: NationCompetitionsListProps) {
  return (
    <div className="mb-10 max-w-2xl mx-auto">
      <h2 className="text-2xl font-semibold text-white mb-3">Competitions</h2>
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="p-4">
          {competitions.length === 0 ? (
            <p className="text-gray-400 text-sm">No competitions found.</p>
          ) : (
            <ul className="divide-y divide-gray-700">
              {competitions.map((competition) => (
                <li key={competition.id} className="py-2 flex items-center justify-between">
                  {competition.has_seasons ? (
                    <Link href={`/leagues/${competition.id}`} className="text-white hover:text-orange-400 transition-colors">
                      {competition.name}
                    </Link>
                  ) : (
                    <span className="text-white">{competition.name}</span>
                  )}
                  <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">{competition.tier || 'Other'}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

