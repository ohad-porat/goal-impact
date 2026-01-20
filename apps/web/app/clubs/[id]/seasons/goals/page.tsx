import { TeamSeasonGoalLogResponse } from "../../../../../lib/types/club";
import { api } from "../../../../../lib/api";
import { ErrorDisplay } from "../../../../../components/ErrorDisplay";
import { TeamSeasonGoalLogTableHeader } from "./components/TeamSeasonGoalLogTableHeader";
import { TeamSeasonGoalLogTableBody } from "./components/TeamSeasonGoalLogTableBody";
import Link from "next/link";

interface GoalLogPageProps {
  params: {
    id: string;
  };
  searchParams: {
    season?: string;
  };
}

async function getTeamSeasonGoalLog(
  teamId: number,
  seasonId: number,
): Promise<TeamSeasonGoalLogResponse> {
  const response = await fetch(api.teamSeasonGoalLog(teamId, seasonId), {
    next: { revalidate: 86400 },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch team season goal log");
  }

  return response.json();
}

const GoalLogContent = ({
  team,
  season,
  competition,
  goals,
  teamId,
  seasonId,
}: {
  team: TeamSeasonGoalLogResponse["team"];
  season: TeamSeasonGoalLogResponse["season"];
  competition: TeamSeasonGoalLogResponse["competition"];
  goals: TeamSeasonGoalLogResponse["goals"];
  teamId: number;
  seasonId: number;
}) => {
  return (
    <div className="min-h-screen">
      <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-white flex-1">
            Goal Log: {team.name} {season.display_name} ({competition.name})
          </h1>
          <Link
            href={`/clubs/${teamId}/seasons?season=${seasonId}`}
            className="px-4 py-2 bg-slate-700 text-white font-semibold rounded-md border border-slate-600 hover:bg-slate-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent whitespace-nowrap flex-shrink-0"
          >
            Back to Roster
          </Link>
        </div>

        <div>
          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700 table-fixed">
                <TeamSeasonGoalLogTableHeader />
                <TeamSeasonGoalLogTableBody goals={goals} />
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default async function GoalLogPage({
  params,
  searchParams,
}: GoalLogPageProps) {
  const [{ id }, { season }] = await Promise.all([params, searchParams]);
  const teamId = parseInt(id);
  const seasonId = season ? parseInt(season) : null;

  if (isNaN(teamId)) {
    return <ErrorDisplay message={`The team ID "${id}" is not valid.`} />;
  }

  if (!seasonId || isNaN(seasonId)) {
    return <ErrorDisplay message="Season parameter is required." />;
  }

  let team: TeamSeasonGoalLogResponse["team"];
  let seasonData: TeamSeasonGoalLogResponse["season"];
  let competition: TeamSeasonGoalLogResponse["competition"];
  let goals: TeamSeasonGoalLogResponse["goals"];

  try {
    const data = await getTeamSeasonGoalLog(teamId, seasonId);
    team = data.team;
    seasonData = data.season;
    competition = data.competition;
    goals = data.goals;
  } catch (error) {
    console.error("Error fetching team season goal log:", error);
    return (
      <ErrorDisplay message="The requested goal log could not be found or does not exist." />
    );
  }

  return (
    <GoalLogContent
      team={team}
      season={seasonData}
      competition={competition}
      goals={goals}
      teamId={teamId}
      seasonId={seasonId}
    />
  );
}
