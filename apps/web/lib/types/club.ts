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

export interface TeamPlayerSeasonStats {
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

export interface PlayerSeasonData {
  player: {
    id: number
    name: string
  }
  stats: TeamPlayerSeasonStats
}

export interface TeamSeasonSquadResponse {
  team: {
    id: number
    name: string
    nation: {
      id: number | null
      name: string
      country_code: string | null
    }
  }
  season: {
    id: number
    start_year: number | null
    end_year: number | null
    display_name: string
  }
  competition: {
    id: number | null
    name: string
  }
  players: PlayerSeasonData[]
}

export interface GoalLogEntry {
  date: string
  venue: string
  scorer: {
    id: number
    name: string
  }
  opponent: {
    id: number
    name: string
    nation: {
      id: number | null
      name: string
      country_code: string | null
    }
  }
  minute: number
  score_before: string
  score_after: string
  goal_value: number | null
  xg: number | null
  post_shot_xg: number | null
  assisted_by: {
    id: number
    name: string
  } | null
}

export interface TeamSeasonGoalLogResponse {
  team: {
    id: number
    name: string
    nation: {
      id: number | null
      name: string
      country_code: string | null
    }
  }
  season: {
    id: number
    start_year: number | null
    end_year: number | null
    display_name: string
  }
  competition: {
    id: number | null
    name: string
  }
  goals: GoalLogEntry[]
}

export interface PlayerGoalLogEntry {
  date: string
  venue: string
  team: {
    id: number
    name: string
    nation: {
      id: number | null
      name: string
      country_code: string | null
    }
  }
  opponent: {
    id: number
    name: string
    nation: {
      id: number | null
      name: string
      country_code: string | null
    }
  }
  minute: number
  score_before: string
  score_after: string
  goal_value: number | null
  xg: number | null
  post_shot_xg: number | null
  assisted_by: {
    id: number
    name: string
  } | null
  season_id: number
  season_display_name: string
}

export interface PlayerGoalLogResponse {
  player: {
    id: number
    name: string
  }
  goals: PlayerGoalLogEntry[]
}
