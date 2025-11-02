export function getShortLeagueName(competitionName: string): string {
  const shortNames: Record<string, string> = {
    'Campeonato Brasileiro Série A': 'Série A',
    'Fußball-Bundesliga': 'Bundesliga',
  }

  return shortNames[competitionName] || competitionName
}
