const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL!

export const api = {
  leagues: `${API_BASE_URL}/leagues/`,
  leagueSeasons: (leagueId: number) => `${API_BASE_URL}/leagues/${leagueId}/seasons`,
  leagueTable: (leagueId: number, seasonId: number) => `${API_BASE_URL}/leagues/${leagueId}/table/${seasonId}`,
  clubs: `${API_BASE_URL}/clubs/`,
  clubDetails: (clubId: number) => `${API_BASE_URL}/clubs/${clubId}`,
  teamSeasonSquad: (teamId: number, seasonId: number) => `${API_BASE_URL}/clubs/${teamId}/seasons/${seasonId}`,
  teamSeasonGoalLog: (teamId: number, seasonId: number) => `${API_BASE_URL}/clubs/${teamId}/seasons/${seasonId}/goals`,
  playerDetails: (playerId: number) => `${API_BASE_URL}/players/${playerId}`,
  playerGoalLog: (playerId: number) => `${API_BASE_URL}/players/${playerId}/goals`,
  nations: `${API_BASE_URL}/nations/`,
  nationDetails: (nationId: number) => `${API_BASE_URL}/nations/${nationId}`,
  leadersCareerTotals: (leagueId?: number) => {
    const url = new URL(`${API_BASE_URL}/leaders/career-totals`)
    if (leagueId !== undefined) {
      url.searchParams.set('league_id', leagueId.toString())
    }
    return url.toString()
  },
  leadersBySeason: (seasonId: number, leagueId?: number) => {
    const url = new URL(`${API_BASE_URL}/leaders/by-season`)
    url.searchParams.set('season_id', seasonId.toString())
    if (leagueId !== undefined) {
      url.searchParams.set('league_id', leagueId.toString())
    }
    return url.toString()
  },
  leadersAllSeasons: (leagueId?: number) => {
    const url = new URL(`${API_BASE_URL}/leaders/all-seasons`)
    if (leagueId !== undefined) {
      url.searchParams.set('league_id', leagueId.toString())
    }
    return url.toString()
  },
  allSeasons: `${API_BASE_URL}/leagues/seasons`,
  recentGoals: (leagueId?: number) => {
    const url = new URL(`${API_BASE_URL}/home/recent-goals`)
    if (leagueId !== undefined) {
      url.searchParams.set('league_id', leagueId.toString())
    }
    return url.toString()
  },
  search: (query: string) => {
    const url = new URL(`${API_BASE_URL}/search/`)
    url.searchParams.set('q', query)
    return url.toString()
  },
}
