import { League } from '../../lib/types'
import { api } from '../../lib/api'

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
  const leagues = await getLeagues()
  
  const classes = {
    header: "px-6 py-3 text-left text-sm font-bold text-white uppercase tracking-wider",
    cell: "px-6 py-4 whitespace-nowrap",
    text: {
      primary: "text-sm font-medium text-white",
      secondary: "text-sm text-gray-300",
      center: "px-6 py-4 text-center text-gray-400"
    }
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Leagues</h1>
        </div>

        <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th className={classes.header}>Name</th>
                  <th className={classes.header}>Country</th>
                  <th className={classes.header}>Gender</th>
                  <th className={classes.header}>Tier</th>
                  <th className={classes.header}>Available Seasons</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {leagues.length === 0 ? (
                  <tr>
                    <td colSpan={5} className={classes.text.center}>
                      No leagues found
                    </td>
                  </tr>
                ) : (
                  leagues.map((league) => (
                    <tr key={league.id} className="hover:bg-slate-700 transition-colors">
                      <td className={classes.cell}>
                        <div className={classes.text.primary}>
                          {league.name}
                        </div>
                      </td>
                      <td className={classes.cell}>
                        <div className={classes.text.secondary}>
                          {league.country}
                        </div>
                      </td>
                      <td className={classes.cell}>
                        <div className={classes.text.secondary}>
                          {league.gender === 'M' ? 'Men' : league.gender === 'F' ? 'Women' : league.gender}
                        </div>
                      </td>
                      <td className={classes.cell}>
                        <div className={classes.text.secondary}>
                          {league.tier || 'N/A'}
                        </div>
                      </td>
                      <td className={classes.cell}>
                        <div className={classes.text.secondary}>
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
