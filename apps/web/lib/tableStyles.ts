export const tableStyles = {
  compact: {
    header: "px-3 py-3 text-center text-sm font-bold text-black uppercase tracking-wider",
    headerLeft: "px-3 py-3 text-left text-sm font-bold text-black uppercase tracking-wider",
    cell: "px-3 py-2 whitespace-nowrap",
    text: {
      primary: "text-sm font-medium text-white",
      secondary: "text-sm text-gray-300",
      center: "px-3 py-2 text-center text-gray-300",
      teamName: "text-base font-medium text-white",
      points: "px-3 py-2 text-center text-white font-bold"
    }
  },
  
  standard: {
    header: "px-6 py-3 text-left text-sm font-bold text-white uppercase tracking-wider",
    cell: "px-6 py-4 whitespace-nowrap",
    text: {
      primary: "text-sm font-medium text-white",
      secondary: "text-sm text-gray-300",
      center: "px-6 py-4 text-center text-gray-400"
    }
  }
}

export const leagueTableColumns = [
  { key: 'position', label: 'Pos', align: 'left' },
  { key: 'team_name', label: 'Club', align: 'left' },
  { key: 'matches_played', label: 'MP', align: 'center' },
  { key: 'wins', label: 'W', align: 'center' },
  { key: 'draws', label: 'D', align: 'center' },
  { key: 'losses', label: 'L', align: 'center' },
  { key: 'goals_for', label: 'GF', align: 'center' },
  { key: 'goals_against', label: 'GA', align: 'center' },
  { key: 'goal_difference', label: 'GD', align: 'center' },
  { key: 'points', label: 'Pts', align: 'center' }
]
