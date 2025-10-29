/**
 * Returns a shortened version of league names for display in tables.
 * This keeps the UI clean and readable by removing redundant prefixes.
 */
export function getShortLeagueName(competitionName: string): string {
  const shortNames: Record<string, string> = {
    'Campeonato Brasileiro Série A': 'Série A',
    'Fußball-Bundesliga': 'Bundesliga',
  }

  return shortNames[competitionName] || competitionName
}
