export interface League {
  id: number;
  name: string;
  country: string;
  gender: string;
  tier: string;
  available_seasons: string;
}

export interface Season {
  id: number;
  start_year: number;
  end_year: number;
  display_name: string;
}

export interface TeamTableEntry {
  position: number;
  team_id: number;
  team_name: string;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
}

export interface LeagueTableData {
  league: {
    id: number;
    name: string;
    country: string;
  };
  season: {
    id: number;
    start_year: number;
    end_year: number;
    display_name: string;
  };
  table: TeamTableEntry[];
}
