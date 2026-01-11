export interface NationInfo {
  id: number | null
  name: string | null
  country_code: string | null
}

export interface CareerTotalsPlayer {
  player_id: number
  player_name: string
  nation: NationInfo | null
  total_goal_value: number
  goal_value_avg: number
  total_goals: number
  total_matches: number
}

export interface CareerTotalsResponse {
  top_goal_value: CareerTotalsPlayer[]
}

export interface BySeasonPlayer {
  player_id: number
  player_name: string
  clubs: string
  total_goal_value: number
  goal_value_avg: number
  total_goals: number
  total_matches: number
}

export interface BySeasonResponse {
  top_goal_value: BySeasonPlayer[]
}

export interface AllSeasonsPlayer {
  player_id: number
  player_name: string
  season_id: number
  season_display_name: string
  clubs: string
  total_goal_value: number
  goal_value_avg: number
  total_goals: number
  total_matches: number
}

export interface AllSeasonsResponse {
  top_goal_value: AllSeasonsPlayer[]
}
