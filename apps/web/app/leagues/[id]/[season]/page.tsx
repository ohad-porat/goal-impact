import { redirect } from 'next/navigation'
import { LeagueTableData, Season } from '../../../../lib/types'
import { api } from '../../../../lib/api'
import LeagueShowClient from '../LeagueShowClient'

async function getLeagueSeasons(leagueId: number): Promise<Season[]> {
  const response = await fetch(api.leagueSeasons(leagueId), {
    cache: 'force-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch league seasons')
  }
  
  const data = await response.json()
  return data.seasons
}

async function getLeagueTable(leagueId: number, seasonId: number): Promise<LeagueTableData> {
  const response = await fetch(api.leagueTable(leagueId, seasonId), {
    cache: 'force-cache'
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch league table')
  }
  
  return response.json()
}

interface LeagueSeasonPageProps {
  params: {
    id: string
    season: string
  }
}

export default async function LeagueSeasonPage({ params }: LeagueSeasonPageProps) {
  const leagueId = parseInt(params.id)
  const seasonId = parseInt(params.season)
  
  if (isNaN(leagueId) || isNaN(seasonId)) {
    redirect('/leagues')
  }

  try {
    const seasons = await getLeagueSeasons(leagueId)
    
    if (seasons.length === 0) {
      redirect('/leagues')
    }

    const requestedSeason = seasons.find(s => s.id === seasonId)
    if (!requestedSeason) {
      redirect(`/leagues/${leagueId}`)
    }
    
    const leagueTableData = await getLeagueTable(leagueId, seasonId)
    
    return (
      <LeagueShowClient 
        initialData={leagueTableData}
        seasons={seasons}
        leagueId={leagueId}
      />
    )
  } catch (error) {
    console.error('Error fetching league data:', error)
    redirect('/leagues')
  }
}
