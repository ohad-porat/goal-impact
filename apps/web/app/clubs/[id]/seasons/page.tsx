import { TeamSeasonSquadResponse } from "../../../../lib/types/club";
import { api } from "../../../../lib/api";
import { ErrorDisplay } from "../../../../components/ErrorDisplay";
import { TeamSeasonRosterTableHeader } from "./components/TeamSeasonRosterTableHeader";
import { TeamSeasonRosterTableBody } from "./components/TeamSeasonRosterTableBody";
import Link from "next/link";

interface TeamSeasonPageProps {
  params: {
    id: string;
  };
  searchParams: {
    season?: string;
  };
}

async function getTeamSeasonSquad(
  teamId: number,
  seasonId: number,
): Promise<TeamSeasonSquadResponse> {
  const response = await fetch(api.teamSeasonSquad(teamId, seasonId), {
    next: { revalidate: 86400 },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch team season squad");
  }

  return response.json();
}

const TeamSeasonContent = ({
  team,
  season,
  competition,
  players,
  teamId,
  seasonId,
}: {
  team: TeamSeasonSquadResponse["team"];
  season: TeamSeasonSquadResponse["season"];
  competition: TeamSeasonSquadResponse["competition"];
  players: TeamSeasonSquadResponse["players"];
  teamId: number;
  seasonId: number;
}) => {
  return (
    <div className="min-h-screen">
      <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-white flex-1 min-w-0">
            {team.name} {season.display_name} ({competition.name})
          </h1>
          <Link
            href={`/clubs/${teamId}/seasons/goals?season=${seasonId}`}
            className="px-4 py-2 bg-slate-700 text-white font-semibold rounded-md border border-slate-600 hover:bg-slate-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent whitespace-nowrap flex-shrink-0"
          >
            View Goal Log
          </Link>
        </div>

        <div>
          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700 table-fixed">
                <TeamSeasonRosterTableHeader />
                <TeamSeasonRosterTableBody players={players} />
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default async function TeamSeasonPage({
  params,
  searchParams,
}: TeamSeasonPageProps) {
  const [{ id }, { season }] = await Promise.all([params, searchParams]);
  const teamId = parseInt(id);
  const seasonId = season ? parseInt(season) : null;

  if (isNaN(teamId)) {
    return <ErrorDisplay message={`The team ID "${id}" is not valid.`} />;
  }

  if (!seasonId || isNaN(seasonId)) {
    return <ErrorDisplay message="Season parameter is required." />;
  }

  let team: TeamSeasonSquadResponse["team"];
  let seasonData: TeamSeasonSquadResponse["season"];
  let competition: TeamSeasonSquadResponse["competition"];
  let players: TeamSeasonSquadResponse["players"];

  try {
    const data = await getTeamSeasonSquad(teamId, seasonId);
    team = data.team;
    seasonData = data.season;
    competition = data.competition;
    players = data.players;
  } catch (error) {
    console.error("Error fetching team season squad:", error);
    return (
      <ErrorDisplay message="The requested team season could not be found or does not exist." />
    );
  }

  return (
    <TeamSeasonContent
      team={team}
      season={seasonData}
      competition={competition}
      players={players}
      teamId={teamId}
      seasonId={seasonId}
    />
  );
}
