export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-900 mb-6">
            Goal Impact
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Advanced soccer data analytics platform featuring proprietary Goal Value (GV) 
            and Points Added (PA) metrics for comprehensive player and team analysis.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Player Analytics</h3>
              <p className="text-gray-600">
                Deep dive into individual player performance with Goal Value metrics 
                and comprehensive statistical analysis.
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Team Performance</h3>
              <p className="text-gray-600">
                Analyze team dynamics and collective impact through Points Added 
                calculations and tactical insights.
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Match Analysis</h3>
              <p className="text-gray-600">
                Comprehensive match breakdowns with event tracking and 
                probability-based goal impact calculations.
              </p>
            </div>
          </div>
          
          <div className="mt-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Supported Leagues
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              {[
                'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1',
                'Eredivisie', 'Primeira Liga', 'MLS', 'Champions League', 'Europa League'
              ].map((league) => (
                <div key={league} className="bg-white rounded-lg p-3 shadow">
                  {league}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
