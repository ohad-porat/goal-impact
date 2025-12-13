'use client'

import { useRouter, usePathname } from 'next/navigation'

interface Season {
  id: number
  display_name: string
}

interface SeasonSelectorProps {
  seasons: Season[]
  selectedSeasonId: number | null
}

export function SeasonSelector({ seasons, selectedSeasonId }: SeasonSelectorProps) {
  const router = useRouter()
  const pathname = usePathname()

  const handleSeasonChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const seasonId = event.target.value
    const params = new URLSearchParams()
    params.set('season', seasonId)
    
    router.push(`${pathname}?${params.toString()}`, { scroll: false })
  }

  if (!selectedSeasonId) {
    return null
  }

  return (
    <select
      value={selectedSeasonId.toString()}
      onChange={handleSeasonChange}
      className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent w-full sm:w-auto"
    >
      {seasons.map((season) => (
        <option key={season.id} value={season.id.toString()}>
          {season.display_name}
        </option>
      ))}
    </select>
  )
}
