import { League } from '../lib/types/league'
import { api } from '../lib/api'
import { ErrorDisplay } from '../components/ErrorDisplay'
import { RecentImpactGoals } from './components/RecentImpactGoals'
import { RecentImpactGoalsResponse } from '../lib/types/home'

async function getLeagues(): Promise<League[]> {
  const response = await fetch(api.leagues, {
    next: { revalidate: 86400 }
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch leagues')
  }
  
  const data = await response.json()
  return data.leagues
}

async function getRecentGoals(): Promise<RecentImpactGoalsResponse> {
  const response = await fetch(api.recentGoals(), {
    next: { revalidate: 300 }
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch recent goals')
  }
  
  return response.json()
}

export default async function HomePage() {
  let leagues: League[] = []
  let initialGoals: RecentImpactGoalsResponse | null = null
  
  const [leaguesResult, goalsResult] = await Promise.allSettled([
    getLeagues(),
    getRecentGoals()
  ])
  
  if (leaguesResult.status === 'fulfilled') {
    leagues = leaguesResult.value
  } else {
    return <ErrorDisplay message="Failed to load leagues." />
  }
  
  if (goalsResult.status === 'fulfilled') {
    initialGoals = goalsResult.value
  }

  return (
    <div className="bg-slate-900 min-h-screen">
      <section className="flex items-center justify-center px-4">
        <div className="text-center max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Evaluate soccer's most valuable goals
          </h1>
          <p className="text-xl md:text-2xl text-white mb-10 font-normal max-w-3xl mx-auto">
            Goal Value measures the significance of every goal
          </p>
        </div>
      </section>

      <RecentImpactGoals initialLeagues={leagues} initialGoals={initialGoals} />

      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <h2 className="text-4xl font-bold text-white mb-6">How it works</h2>
        <div className="text-white text-lg max-w-4xl space-y-4">
          <p>
            <strong>Goal Value</strong> measures how much a goal changes a team's win probability based on the context in which it was scored. Not all goals are created equal—a last-minute equalizer is worth more than a goal that makes it 4-0.
          </p>
          <p>
            The metric is calculated by analyzing historical match data across thousands of games. For each goal, we look at:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>When it was scored:</strong> A goal in the 90th minute has more value than one in the 10th minute</li>
            <li><strong>The score difference:</strong> Equalizing from 0-1 down is more valuable than extending a 3-0 lead</li>
            <li><strong>Match outcome:</strong> Whether the team that scored the goal went on to win, draw, or lose</li>
          </ul>
          <p>
            By aggregating historical outcomes for similar situations (same minute, same score difference), we calculate the expected change in win probability for each goal. A Goal Value of +0.64 means that goal increased the team's win probability by 64 percentage points on average.
          </p>
          <p>
            This allows us to identify which goals truly mattered—those that turned defeats into draws, draws into wins, or secured crucial victories when it mattered most.
          </p>
        </div>
      </section>
    </div>
  )
}
