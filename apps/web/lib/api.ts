const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL!

export const api = {
  leagues: `${API_BASE_URL}/leagues/`,
  leagueSeasons: (leagueId: number) => `${API_BASE_URL}/leagues/${leagueId}/seasons`,
  leagueTable: (leagueId: number, seasonId: number) => `${API_BASE_URL}/leagues/${leagueId}/table/${seasonId}`,
  clubs: `${API_BASE_URL}/clubs/`,
  clubDetails: (clubId: number) => `${API_BASE_URL}/clubs/${clubId}`,
}
