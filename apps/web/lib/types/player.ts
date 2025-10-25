export interface PlayerSeasonStats {
  matches_played: number | null
  matches_started: number | null
  total_minutes: number | null
  minutes_divided_90: number | null
  goals_scored: number | null
  assists: number | null
  total_goal_assists: number | null
  non_pk_goals: number | null
  pk_made: number | null
  pk_attempted: number | null
  yellow_cards: number | null
  red_cards: number | null
  goal_value: number | null
  gv_avg: number | null
  goal_per_90: number | null
  assists_per_90: number | null
  total_goals_assists_per_90: number | null
  non_pk_goals_per_90: number | null
  non_pk_goal_and_assists_per_90: number | null
}

export interface PlayerSeasonRecord {
  season: {
    id: number
    start_year: number | null
    end_year: number | null
    display_name: string
  }
  team: {
    id: number
    name: string
  }
  competition: {
    id: number
    name: string
  }
  league_rank: number | null
  stats: PlayerSeasonStats
}

export interface PlayerDetailsResponse {
  player: {
    id: number
    name: string
    nation: {
      id: number | null
      name: string | null
      country_code: string | null
    }
  }
  seasons: PlayerSeasonRecord[]
}

