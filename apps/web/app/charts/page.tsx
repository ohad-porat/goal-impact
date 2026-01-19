'use client'

import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { useSearchParams, useRouter } from 'next/navigation'
import { CareerTotalsScatterChart } from './components/CareerTotalsScatterChart'

// Dynamically import ComparePlayersRadarChart with SSR disabled to avoid hydration mismatches
// caused by browser extensions modifying form inputs
const ComparePlayersRadarChart = dynamic(
  () => import('./components/ComparePlayersRadarChart').then((mod) => ({ default: mod.ComparePlayersRadarChart })),
  { ssr: false }
)

type TabType = 'career' | 'compare'

const TABS: { id: TabType; label: string }[] = [
  { id: 'career', label: 'Career Totals' },
  { id: 'compare', label: 'Compare Players' },
]

const isValidTab = (tab: string | null): tab is TabType => {
  return tab === 'career' || tab === 'compare'
}

function ChartsPageContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const viewParam = searchParams.get('view')
  const activeTab = isValidTab(viewParam) ? viewParam : 'career'

  const handleTabChange = (tab: TabType) => {
    router.push(`/charts?view=${tab}`, { scroll: false })
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-6">Charts</h1>
          
          <div className="inline-flex space-x-1 bg-slate-800 rounded-lg p-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`
                  px-4 py-2 rounded-md font-semibold text-sm transition-colors whitespace-nowrap
                  ${
                    activeTab === tab.id
                      ? 'bg-orange-400 text-black'
                      : 'text-gray-300 hover:text-white hover:bg-slate-700'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-8">
          {activeTab === 'career' && <CareerTotalsScatterChart />}
          {activeTab === 'compare' && <ComparePlayersRadarChart />}
        </div>
      </div>
    </div>
  )
}

export default function ChartsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    }>
      <ChartsPageContent />
    </Suspense>
  )
}
