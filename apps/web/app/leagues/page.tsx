import Link from 'next/link'
import { League } from '../../lib/types'
import { api } from '../../lib/api'
import { tableStyles } from '../../lib/tableStyles'
import { ErrorDisplay } from '../../components/ErrorDisplay'

async function getLeagues(): Promise<League[]> {
  const response = await fetch(api.leagues, {
    cache: 'force-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch leagues')
  }
  
  const data = await response.json()
  return data.leagues
}

export default async function LeaguesPage() {
  let leagues: League[] = []
  try {
    leagues = await getLeagues()
  } catch (error) {
    return <ErrorDisplay message="Failed to load leagues." />
  }
  
  const styles = tableStyles.standard

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-white">Leagues</h1>
        </div>

        <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th className={styles.header}>Name</th>
                  <th className={styles.header}>Country</th>
                  <th className={styles.header}>Gender</th>
                  <th className={styles.header}>Tier</th>
                  <th className={styles.header}>Available Seasons</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {leagues.length === 0 ? (
                  <tr>
                    <td colSpan={5} className={styles.text.center}>
                      No leagues found
                    </td>
                  </tr>
                ) : (
                  leagues.map((league) => (
                    <tr key={league.id} className="hover:bg-slate-700 transition-colors">
                      <td className={styles.cell}>
                        <Link href={`/leagues/${league.id}`} className="hover:text-orange-400 transition-colors">
                          <div className={styles.text.primary}>
                            {league.name}
                          </div>
                        </Link>
                      </td>
                      <td className={styles.cell}>
                        <div className={styles.text.secondary}>
                          {league.country}
                        </div>
                      </td>
                      <td className={styles.cell}>
                        <div className={styles.text.secondary}>
                          {league.gender === 'M' ? 'Men' : league.gender === 'F' ? 'Women' : league.gender}
                        </div>
                      </td>
                      <td className={styles.cell}>
                        <div className={styles.text.secondary}>
                          {league.tier || 'N/A'}
                        </div>
                      </td>
                      <td className={styles.cell}>
                        <div className={styles.text.secondary}>
                          {league.available_seasons}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
