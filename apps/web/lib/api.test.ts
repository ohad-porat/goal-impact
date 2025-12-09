import { describe, it, expect, beforeEach, vi } from 'vitest'
import type { api as ApiType } from './api'

const mockApiBaseUrl = 'https://api.example.com'

describe('API Client', () => {
  let api: typeof ApiType

  beforeEach(async () => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', mockApiBaseUrl)
    vi.resetModules()
    const apiModule = await import('./api')
    api = apiModule.api
  })

  describe('Simple endpoints (no parameters)', () => {
    it('should construct leagues endpoint', () => {
      expect(api.leagues).toBe(`${mockApiBaseUrl}/leagues/`)
    })

    it('should construct clubs endpoint', () => {
      expect(api.clubs).toBe(`${mockApiBaseUrl}/clubs/`)
    })

    it('should construct nations endpoint', () => {
      expect(api.nations).toBe(`${mockApiBaseUrl}/nations/`)
    })

    it('should construct allSeasons endpoint', () => {
      expect(api.allSeasons).toBe(`${mockApiBaseUrl}/leagues/seasons`)
    })
  })

  describe('Path parameter endpoints', () => {
    it('should construct leagueSeasons with leagueId', () => {
      expect(api.leagueSeasons(123)).toBe(`${mockApiBaseUrl}/leagues/123/seasons`)
    })

    it('should construct leagueTable with leagueId and seasonId', () => {
      expect(api.leagueTable(5, 10)).toBe(`${mockApiBaseUrl}/leagues/5/table/10`)
    })

    it('should construct clubDetails with clubId', () => {
      expect(api.clubDetails(42)).toBe(`${mockApiBaseUrl}/clubs/42`)
    })

    it('should construct teamSeasonSquad with teamId and seasonId', () => {
      expect(api.teamSeasonSquad(7, 15)).toBe(`${mockApiBaseUrl}/clubs/7/seasons/15`)
    })

    it('should construct teamSeasonGoalLog with teamId and seasonId', () => {
      expect(api.teamSeasonGoalLog(8, 20)).toBe(`${mockApiBaseUrl}/clubs/8/seasons/20/goals`)
    })

    it('should construct playerDetails with playerId', () => {
      expect(api.playerDetails(99)).toBe(`${mockApiBaseUrl}/players/99`)
    })

    it('should construct playerGoalLog with playerId', () => {
      expect(api.playerGoalLog(101)).toBe(`${mockApiBaseUrl}/players/101/goals`)
    })

    it('should construct nationDetails with nationId', () => {
      expect(api.nationDetails(3)).toBe(`${mockApiBaseUrl}/nations/3`)
    })
  })

  describe('Query parameter endpoints', () => {
    it('should construct leadersCareerTotals without leagueId', () => {
      expect(api.leadersCareerTotals()).toBe(`${mockApiBaseUrl}/leaders/career-totals`)
    })

    it('should construct leadersCareerTotals with leagueId', () => {
      expect(api.leadersCareerTotals(5)).toBe(`${mockApiBaseUrl}/leaders/career-totals?league_id=5`)
    })

    it('should construct leadersBySeason with seasonId only', () => {
      expect(api.leadersBySeason(10)).toBe(`${mockApiBaseUrl}/leaders/by-season?season_id=10`)
    })

    it('should construct leadersBySeason with seasonId and leagueId', () => {
      expect(api.leadersBySeason(10, 5)).toBe(`${mockApiBaseUrl}/leaders/by-season?season_id=10&league_id=5`)
    })

    it('should construct recentGoals without leagueId', () => {
      expect(api.recentGoals()).toBe(`${mockApiBaseUrl}/home/recent-goals`)
    })

    it('should construct recentGoals with leagueId', () => {
      expect(api.recentGoals(7)).toBe(`${mockApiBaseUrl}/home/recent-goals?league_id=7`)
    })
  })

  describe('Search endpoint', () => {
    it('should construct search endpoint with query', () => {
      expect(api.search('messi')).toBe(`${mockApiBaseUrl}/search/?q=messi`)
    })

    it('should URL encode special characters in search query', () => {
      const query = 'messi & ronaldo'
      const result = api.search(query)
      const url = new URL(result)
      expect(url.searchParams.get('q')).toBe('messi & ronaldo')
    })

    it('should handle empty search query', () => {
      expect(api.search('')).toBe(`${mockApiBaseUrl}/search/?q=`)
    })
  })

  describe('Edge cases', () => {
    it('should handle leagueId as 0 in query params', () => {
      expect(api.leadersCareerTotals(0)).toBe(`${mockApiBaseUrl}/leaders/career-totals?league_id=0`)
    })
  })

  describe('Error handling', () => {
    it('should throw error when NEXT_PUBLIC_API_URL is undefined', async () => {
      const originalValue = process.env.NEXT_PUBLIC_API_URL
      
      delete process.env.NEXT_PUBLIC_API_URL
      vi.resetModules()
      
      const apiModule = await import('./api')
      expect(() => {
        apiModule.api.leadersCareerTotals()
      }).toThrow()
      
      if (originalValue !== undefined) {
        process.env.NEXT_PUBLIC_API_URL = originalValue
      }
    })
  })
})
