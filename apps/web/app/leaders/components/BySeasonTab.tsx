'use client'

import { getShortLeagueName } from '../../../lib/utils'
import { BySeasonTableHeader } from './BySeasonTableHeader'
import { BySeasonTableBody } from './BySeasonTableBody'
import { LeadersTable } from './LeadersTable'
import { useLeagues } from '../hooks/useLeagues'
import { useSeasons } from '../hooks/useSeasons'
import { useBySeasonData } from '../hooks/useBySeasonData'
import { useLeaderFilters } from '../hooks/useLeaderFilters'

export function BySeasonTab() {
  const { leagues, loading: loadingLeagues } = useLeagues()
  const { leagueId, seasonId, selectedLeagueId, selectedSeasonId, updateParams } = useLeaderFilters()
  const { seasons, loading: loadingSeasons } = useSeasons(leagueId)
  const { data: bySeason, error } = useBySeasonData(seasonId, leagueId)

  const handleLeagueChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLeagueId = event.target.value === '' ? null : event.target.value
    updateParams('season', { league_id: newLeagueId, season_id: null })
  }

  const handleSeasonChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newSeasonId = event.target.value || null
    updateParams('season', { season_id: newSeasonId })
  }

  const isEmpty = bySeason !== null && bySeason.top_goal_value.length === 0
  const shouldRenderTable = bySeason !== null || error

  return (
    <div>
      <div className="mb-4 flex items-center justify-between flex-wrap gap-4">
        <h2 className="text-2xl font-bold text-white">Season Leaders by Goal Value</h2>
        <div className="flex gap-4">
          <select
            id="league-filter"
            value={selectedLeagueId || ''}
            onChange={handleLeagueChange}
            className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            disabled={loadingLeagues}
          >
            <option value="">All Leagues</option>
            {leagues.map((league) => (
              <option key={league.id} value={league.id.toString()}>
                {getShortLeagueName(league.name)}
              </option>
            ))}
          </select>
          <select
            id="season-filter"
            value={selectedSeasonId || ''}
            onChange={handleSeasonChange}
            className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            disabled={loadingSeasons || !seasons.length}
          >
            {!seasons.length && <option value="">Loading seasons...</option>}
            {seasons.map((season) => (
              <option key={season.id} value={season.id.toString()}>
                {season.display_name}
              </option>
            ))}
          </select>
        </div>
      </div>
      {shouldRenderTable ? (
        <LeadersTable
          title=""
          header={<BySeasonTableHeader />}
          body={<BySeasonTableBody players={bySeason?.top_goal_value || []} />}
          error={error}
          isEmpty={isEmpty}
        />
      ) : null}
    </div>
  )
}
