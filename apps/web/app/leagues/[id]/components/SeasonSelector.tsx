'use client'

import { useRouter } from 'next/navigation'
import { Season } from '../../../../lib/types'

interface SeasonSelectorProps {
  seasons: Season[]
  currentSeasonId: number
  leagueId: number
}

export function SeasonSelector({ seasons, currentSeasonId, leagueId }: SeasonSelectorProps) {
  const router = useRouter()

  const handleSeasonChange = (newSeasonId: number) => {
    router.replace(`/leagues/${leagueId}?season=${newSeasonId}`, { scroll: false })
  }

  return (
    <select
      value={currentSeasonId}
      onChange={(e) => handleSeasonChange(parseInt(e.target.value))}
      className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-orange-500 focus:outline-none"
    >
      {seasons.map((season) => (
        <option key={season.id} value={season.id}>
          {season.display_name}
        </option>
      ))}
    </select>
  )
}
