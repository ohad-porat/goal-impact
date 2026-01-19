export interface RecentGoalPlayer {
  id: number;
  name: string;
}

export interface RecentGoalMatch {
  home_team: string;
  away_team: string;
  date: string;
}

export interface RecentImpactGoal {
  match: RecentGoalMatch;
  scorer: RecentGoalPlayer;
  minute: number;
  goal_value: number;
  score_before: string;
  score_after: string;
}

export interface RecentImpactGoalsResponse {
  goals: RecentImpactGoal[];
}
