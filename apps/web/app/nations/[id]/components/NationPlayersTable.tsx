import Link from 'next/link'
import { NationPlayerSummary } from '../../../../lib/types/nation'

interface NationPlayersTableProps {
  players: NationPlayerSummary[]
}

export function NationPlayersTable({ players }: NationPlayersTableProps) {
  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl sm:text-2xl font-semibold text-white mb-3">Top Players</h2>
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700 table-fixed">
            <thead className="bg-gray-700">
              <tr>
                <th className="pl-6 pr-3 py-3 text-left text-sm font-bold text-white uppercase tracking-wider">Player</th>
                <th className="px-3 py-3 text-center w-32 whitespace-nowrap text-sm font-bold text-white uppercase tracking-wider">Career GV</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {players.length === 0 ? (
                <tr>
                  <td colSpan={2} className="px-4 py-4 text-center text-gray-400 text-sm">No players found.</td>
                </tr>
              ) : (
                players.map((player) => (
                  <tr key={player.id} className="hover:bg-slate-700 transition-colors">
                    <td className="pl-6 pr-3 py-2 whitespace-nowrap">
                      <Link href={`/players/${player.id}`} className="text-white hover:text-orange-400 transition-colors">
                        {player.name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-center w-32 whitespace-nowrap text-white">
                      {(player.total_goal_value ?? 0).toFixed(2)}
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

