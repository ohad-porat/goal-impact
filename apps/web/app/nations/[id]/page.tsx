import { api } from "../../../lib/api";
import { NationDetailsResponse } from "../../../lib/types/nation";
import { ErrorDisplay } from "../../../components/ErrorDisplay";
import { NationCompetitionsList } from "./components/NationCompetitionsList";
import { NationClubsTable } from "./components/NationClubsTable";
import { NationPlayersTable } from "./components/NationPlayersTable";

interface NationShowPageProps {
  params: { id: string };
}

async function getNationDetails(
  nationId: number,
): Promise<NationDetailsResponse> {
  const response = await fetch(api.nationDetails(nationId), {
    next: { revalidate: 86400 },
  });
  if (!response.ok) {
    throw new Error("Failed to fetch nation details");
  }
  return response.json();
}

const NationDetailsContent = ({
  nation,
  competitions,
  clubs,
  players,
}: {
  nation: NationDetailsResponse["nation"];
  competitions: NationDetailsResponse["competitions"];
  clubs: NationDetailsResponse["clubs"];
  players: NationDetailsResponse["players"];
}) => {
  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white">
            {nation.name}
          </h1>
          <p className="text-gray-400 mt-1 text-sm sm:text-base">
            FIFA Code: {nation.country_code} • Governing Body:{" "}
            {nation.governing_body}
          </p>
        </div>

        <NationCompetitionsList competitions={competitions} />
        <NationClubsTable clubs={clubs} />
        <NationPlayersTable players={players} />
      </div>
    </div>
  );
};

export default async function NationShowPage({ params }: NationShowPageProps) {
  const { id } = await params;
  const nationId = parseInt(id);
  if (isNaN(nationId)) {
    return <ErrorDisplay message={`The nation ID "${id}" is not valid.`} />;
  }

  let nation: NationDetailsResponse["nation"];
  let competitions: NationDetailsResponse["competitions"];
  let clubs: NationDetailsResponse["clubs"];
  let players: NationDetailsResponse["players"];

  try {
    const data = await getNationDetails(nationId);
    nation = data.nation;
    competitions = data.competitions;
    clubs = data.clubs;
    players = data.players;
  } catch (error) {
    console.error("Error fetching nation details:", error);
    return (
      <ErrorDisplay message="The requested nation could not be found or does not exist." />
    );
  }

  return (
    <NationDetailsContent
      nation={nation}
      competitions={competitions}
      clubs={clubs}
      players={players}
    />
  );
}
