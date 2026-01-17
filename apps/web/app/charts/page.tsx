'use client'

import { Suspense } from 'react'
import { CareerTotalsScatterChart } from './components/CareerTotalsScatterChart'

function ChartsPageContent() {
  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-6">Charts</h1>
        </div>

        <div className="mt-8">
          <CareerTotalsScatterChart />
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
