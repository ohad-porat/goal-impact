import Link from 'next/link'
import { NationClubSummary } from '../../../../lib/types/nation'

interface NationClubsTableProps {
  clubs: NationClubSummary[]
}

export function NationClubsTable({ clubs }: NationClubsTableProps) {
  return (
    <div className="mb-10 max-w-2xl mx-auto">
      <h2 className="text-2xl font-semibold text-white mb-3">Top Clubs</h2>
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700 table-fixed">
            <thead className="bg-gray-700">
              <tr>
                <th className="pl-6 pr-3 py-3 text-left text-sm font-bold text-white uppercase tracking-wider">Club</th>
                <th className="px-3 py-3 text-center w-32 whitespace-nowrap text-sm font-bold text-white uppercase tracking-wider">Avg Pos</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {clubs.length === 0 ? (
                <tr>
                  <td colSpan={2} className="px-4 py-4 text-center text-gray-400 text-sm">No qualifying clubs found.</td>
                </tr>
              ) : (
                clubs.map((club) => (
                  <tr key={club.id} className="hover:bg-slate-700 transition-colors">
                    <td className="pl-6 pr-3 py-2 whitespace-nowrap">
                      {club.has_stats ? (
                        <Link href={`/clubs/${club.id}`} className="text-white hover:text-orange-400 transition-colors">
                          {club.name}
                        </Link>
                      ) : (
                        <span className="text-white">{club.name}</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-center w-32 whitespace-nowrap text-white">
                      {club.avg_position !== null && club.avg_position !== undefined ? club.avg_position.toFixed(1) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

