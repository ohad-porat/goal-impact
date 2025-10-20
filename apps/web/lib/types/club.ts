export interface Club {
  id: number
  name: string
  avg_position: number
}

export interface NationWithClubs {
  nation: {
    id: number
    name: string
    country_code: string
  }
  clubs: Club[]
}

export interface ClubsResponse {
  nations: NationWithClubs[]
}

export interface ClubSeasonStats {
  ranking: number | null
  matches_played: number | null
  wins: number | null
  draws: number | null
  losses: number | null
  goals_for: number | null
  goals_against: number | null
  goal_difference: number | null
  points: number | null
  attendance: number | null
  notes: string | null
}

export interface ClubSeason {
  season: {
    id: number
    start_year: number | null
    end_year: number | null
    year_range: string
  }
  competition: {
    id: number
    name: string | null
    tier: string | null
  }
  stats: ClubSeasonStats
}

export interface ClubDetails {
  club: {
    id: number
    name: string | null
    nation: {
      id: number
      name: string | null
      country_code: string | null
    }
  }
  seasons: ClubSeason[]
}

export interface ClubDetailsResponse {
  club: ClubDetails['club']
  seasons: ClubDetails['seasons']
}
