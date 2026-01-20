export function getShortLeagueName(competitionName: string): string {
  const shortNames: Record<string, string> = {
    "Campeonato Brasileiro Série A": "Série A",
    "Fußball-Bundesliga": "Bundesliga",
  };

  if (competitionName === null || competitionName === undefined) {
    return "";
  }

  const trimmedName = competitionName.trim();
  return shortNames[trimmedName] || trimmedName;
}
