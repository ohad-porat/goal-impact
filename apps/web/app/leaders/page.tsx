'use client'

import { useSearchParams, useRouter } from 'next/navigation'
import { CareerTotalsTab } from './components/CareerTotalsTab'
import { BySeasonTab } from './components/BySeasonTab'

type TabType = 'career' | 'season' | 'team'

const TABS: { id: TabType; label: string }[] = [
  { id: 'career', label: 'Career Totals' },
  { id: 'season', label: 'By Season' },
  { id: 'team', label: 'By Team' },
]

const isValidTab = (value: string | null): value is TabType => {
  return value === 'career' || value === 'season' || value === 'team'
}

function LeadersPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const viewParam = searchParams.get('view')
  const activeTab = isValidTab(viewParam) ? viewParam : 'career'

  const handleTabChange = (tab: TabType) => {
    router.push(`/leaders?view=${tab}`, { scroll: false })
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-6">Leaders</h1>
          
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
          {activeTab === 'career' && <CareerTotalsTab />}
          {activeTab === 'season' && <BySeasonTab />}
          {activeTab === 'team' && (
            <div className="text-white text-center">
              <p>By Team content will go here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default LeadersPage
