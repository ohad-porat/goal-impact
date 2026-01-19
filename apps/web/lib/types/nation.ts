export interface Nation {
  id: number;
  name: string;
  country_code: string;
  governing_body: string;
  player_count: number;
}

export interface NationsResponse {
  nations: Nation[];
}

export interface NationCompetition {
  id: number;
  name: string;
  tier: string | null;
  season_count: number;
  has_seasons: boolean;
}

export interface NationClubSummary {
  id: number;
  name: string;
  avg_position: number | null;
}

export interface NationPlayerSummary {
  id: number;
  name: string;
  total_goal_value: number;
}

export interface NationDetailsResponse {
  nation: {
    id: number;
    name: string;
    country_code: string;
    governing_body: string;
  };
  competitions: NationCompetition[];
  clubs: NationClubSummary[];
  players: NationPlayerSummary[];
}
