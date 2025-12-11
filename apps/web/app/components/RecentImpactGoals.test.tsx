import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import { RecentImpactGoals } from './RecentImpactGoals'
import type { RecentImpactGoalsResponse } from '../../lib/types/home'
import type { League } from '../../lib/types/league'

vi.mock('../../lib/api', () => ({
  api: {
    recentGoals: vi.fn((leagueId?: number) => {
      const url = new URL('https://api.example.com/home/recent-goals')
      if (leagueId !== undefined) {
        url.searchParams.set('league_id', leagueId.toString())
      }
      return url.toString()
    }),
  },
}))

vi.mock('../../lib/utils', () => ({
  getShortLeagueName: vi.fn((name: string) => {
    const shortNames: Record<string, string> = {
      'Campeonato Brasileiro Série A': 'Série A',
      'Fußball-Bundesliga': 'Bundesliga',
    }
    return shortNames[name] || name
  }),
}))

describe('RecentImpactGoals', () => {
  const mockLeagues: League[] = [
    { id: 1, name: 'Premier League', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'England' },
    { id: 2, name: 'Serie A', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Italy' },
    { id: 3, name: 'La Liga', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Spain' },
    { id: 4, name: 'Fußball-Bundesliga', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Germany' },
    { id: 5, name: 'Ligue 1', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'France' },
  ]

  const mockGoals: RecentImpactGoalsResponse = {
    goals: [
      {
        match: {
          home_team: 'Team A',
          away_team: 'Team B',
          date: '2024-01-15',
        },
        scorer: {
          id: 1,
          name: 'Player 1',
        },
        minute: 45,
        score_before: '0-0',
        score_after: '1-0',
        goal_value: 0.64,
      },
      {
        match: {
          home_team: 'Team C',
          away_team: 'Team D',
          date: '2024-01-14',
        },
        scorer: {
          id: 2,
          name: 'Player 2',
        },
        minute: 90,
        score_before: '1-1',
        score_after: '2-1',
        goal_value: 0.85,
      },
    ],
  }

  const mockFilteredGoals: RecentImpactGoalsResponse = {
    goals: [
      {
        match: {
          home_team: 'Team E',
          away_team: 'Team F',
          date: '2024-01-13',
        },
        scorer: {
          id: 3,
          name: 'Player 3',
        },
        minute: 30,
        score_before: '0-1',
        score_after: '1-1',
        goal_value: 0.50,
      },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initial rendering', () => {
    it('should render top 4 league filter buttons', () => {
      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      expect(screen.getByText('Premier League')).toBeInTheDocument()
      expect(screen.getByText('Serie A')).toBeInTheDocument()
      expect(screen.getByText('La Liga')).toBeInTheDocument()
      expect(screen.getByText('Bundesliga')).toBeInTheDocument()
      expect(screen.queryByText('Ligue 1')).not.toBeInTheDocument()
    })

    it('should highlight "All Leagues" button by default', () => {
      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      const allLeaguesButton = screen.getByText('All Leagues')
      expect(allLeaguesButton).toHaveClass('bg-orange-400', 'text-black')
      expect(global.fetch).not.toHaveBeenCalled()
    })
  })

  describe('Goal display', () => {
    it('should display goal information correctly', () => {
      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      expect(screen.getByText('Team A vs Team B')).toBeInTheDocument()
      expect(screen.getByText('2024-01-15')).toBeInTheDocument()
      expect(screen.getByText('Minute 45')).toBeInTheDocument()
      expect(screen.getByText('Player 1')).toBeInTheDocument()
      expect(screen.getByText('0-0 → 1-0')).toBeInTheDocument()
      expect(screen.getByText('+0.64')).toBeInTheDocument()
    })

    it('should handle goals without score information', () => {
      const goalsWithoutScore: RecentImpactGoalsResponse = {
        goals: [
          {
            match: {
              home_team: 'Team A',
              away_team: 'Team B',
              date: '2024-01-15',
            },
            scorer: {
              id: 1,
              name: 'Player 1',
            },
            minute: 45,
            score_before: '',
            score_after: '',
            goal_value: 0.64,
          },
        ],
      }

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={goalsWithoutScore} />)

      expect(screen.getByText('-')).toBeInTheDocument()
    })
  })

  describe('League filtering', () => {
    it('should filter and sort top leagues correctly', () => {
      const leagues: League[] = [
        { id: 5, name: 'Ligue 1', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'France' },
        { id: 2, name: 'Serie A', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Italy' },
        { id: 1, name: 'Premier League', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'England' },
        { id: 3, name: 'La Liga', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Spain' },
        { id: 4, name: 'Fußball-Bundesliga', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Germany' },
      ]

      render(<RecentImpactGoals initialLeagues={leagues} initialGoals={mockGoals} />)

      const buttons = screen.getAllByRole('button')
      const leagueButtons = buttons.filter(btn => btn.textContent !== 'All Leagues')
      
      expect(leagueButtons[0]).toHaveTextContent('Premier League')
      expect(leagueButtons[1]).toHaveTextContent('Serie A')
      expect(leagueButtons[2]).toHaveTextContent('La Liga')
      expect(leagueButtons[3]).toHaveTextContent('Bundesliga')
    })

    it('should reset to "All Leagues" when clicking All Leagues button', async () => {
      const mockFetch = global.fetch as ReturnType<typeof vi.fn>
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockFilteredGoals,
      })

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      const premierLeagueButton = screen.getByText('Premier League')
      const allLeaguesButton = screen.getByText('All Leagues')

      act(() => {
        fireEvent.click(premierLeagueButton)
      })

      await waitFor(() => {
        expect(premierLeagueButton).toHaveClass('bg-orange-400')
        expect(screen.getByText('Team E vs Team F')).toBeInTheDocument()
      })

      act(() => {
        fireEvent.click(allLeaguesButton)
      })

      await waitFor(() => {
        expect(allLeaguesButton).toHaveClass('bg-orange-400')
        expect(premierLeagueButton).toHaveClass('bg-slate-700')
        expect(screen.getByText('Team A vs Team B')).toBeInTheDocument()
        expect(screen.queryByText('Team E vs Team F')).not.toBeInTheDocument()
      })
    })
  })

  describe('Data fetching', () => {
    it('should fetch goals when league is selected', async () => {
      const mockFetch = global.fetch as ReturnType<typeof vi.fn>
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockFilteredGoals,
      })

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      const premierLeagueButton = screen.getByText('Premier League')

      act(() => {
        fireEvent.click(premierLeagueButton)
      })

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('league_id=1'),
          { cache: 'no-cache' }
        )
      })

      await waitFor(() => {
        expect(premierLeagueButton).toHaveClass('bg-orange-400', 'text-black')
        expect(screen.getByText('Team E vs Team F')).toBeInTheDocument()
      })
    })

  })

  describe('Error handling', () => {
    it('should display error message when fetch fails', async () => {
      const mockFetch = global.fetch as ReturnType<typeof vi.fn>
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      const premierLeagueButton = screen.getByText('Premier League')

      act(() => {
        fireEvent.click(premierLeagueButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Failed to load recent goals.')).toBeInTheDocument()
        expect(screen.queryByText('Team A vs Team B')).not.toBeInTheDocument()
      })
    })

    it('should display error message when fetch returns non-ok response', async () => {
      const mockFetch = global.fetch as ReturnType<typeof vi.fn>
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      const premierLeagueButton = screen.getByText('Premier League')

      act(() => {
        fireEvent.click(premierLeagueButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Failed to load recent goals.')).toBeInTheDocument()
        expect(screen.queryByText('Team A vs Team B')).not.toBeInTheDocument()
      })
    })

  })

  describe('Empty state', () => {
    it('should display empty state when goals array is empty', () => {
      const emptyGoals: RecentImpactGoalsResponse = {
        goals: [],
      }

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={emptyGoals} />)

      expect(screen.getByText('No recent goals found')).toBeInTheDocument()
    })

    it('should render nothing when initialGoals is null', () => {
      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={null} />)

      expect(screen.getByText('Recent Impact Goals')).toBeInTheDocument()
      expect(screen.queryByText('No recent goals found')).not.toBeInTheDocument()
      expect(screen.queryByText('Failed to load recent goals.')).not.toBeInTheDocument()
    })

    it('should display empty state after filtering returns empty results', async () => {
      const emptyGoals: RecentImpactGoalsResponse = {
        goals: [],
      }

      const mockFetch = global.fetch as ReturnType<typeof vi.fn>
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => emptyGoals,
      })

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={mockGoals} />)

      const premierLeagueButton = screen.getByText('Premier League')

      act(() => {
        fireEvent.click(premierLeagueButton)
      })

      await waitFor(() => {
        expect(screen.getByText('No recent goals found')).toBeInTheDocument()
      })
    })
  })

  describe('Edge cases', () => {
    it('should handle leagues with fewer than 4 top leagues', () => {
      const fewLeagues: League[] = [
        { id: 1, name: 'Premier League', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'England' },
        { id: 2, name: 'Serie A', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Italy' },
      ]

      render(<RecentImpactGoals initialLeagues={fewLeagues} initialGoals={mockGoals} />)

      expect(screen.getByText('Premier League')).toBeInTheDocument()
      expect(screen.getByText('Serie A')).toBeInTheDocument()
    })

    it('should handle leagues with no top leagues', () => {
      const otherLeagues: League[] = [
        { id: 5, name: 'Ligue 1', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'France' },
        { id: 6, name: 'Eredivisie', gender: 'M', tier: '1', available_seasons: '2020-2024', country: 'Netherlands' },
      ]

      render(<RecentImpactGoals initialLeagues={otherLeagues} initialGoals={mockGoals} />)

      const buttons = screen.getAllByRole('button')
      expect(buttons).toHaveLength(1)
      expect(buttons[0]).toHaveTextContent('All Leagues')
    })

    it('should handle multiple goal value formats', () => {
      const goalsWithVariousValues: RecentImpactGoalsResponse = {
        goals: [
          {
            match: {
              home_team: 'Team A',
              away_team: 'Team B',
              date: '2024-01-15',
            },
            scorer: {
              id: 1,
              name: 'Player 1',
            },
            minute: 45,
            score_before: '0-0',
            score_after: '1-0',
            goal_value: 0.123,
          },
          {
            match: {
              home_team: 'Team C',
              away_team: 'Team D',
              date: '2024-01-14',
            },
            scorer: {
              id: 2,
              name: 'Player 2',
            },
            minute: 90,
            score_before: '1-1',
            score_after: '2-1',
            goal_value: 1.5,
          },
        ],
      }

      render(<RecentImpactGoals initialLeagues={mockLeagues} initialGoals={goalsWithVariousValues} />)

      expect(screen.getByText('+0.12')).toBeInTheDocument()
      expect(screen.getByText('+1.50')).toBeInTheDocument()
    })
  })
})

