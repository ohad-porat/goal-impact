import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useLeagues } from './useLeagues'
import { api } from '../../../lib/api'

vi.mock('../../../lib/api', () => ({
  api: {
    leagues: 'https://api.example.com/leagues/',
  } as any,
}))

describe('useLeagues', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  it('should fetch leagues on mount and update loading state from true to false', async () => {
    const mockLeagues = [
      { id: 1, name: 'Premier League', gender: 'M', tier: '1', available_seasons: '2020-2024' },
      { id: 2, name: 'La Liga', gender: 'M', tier: '1', available_seasons: '2020-2024' },
    ]

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ leagues: mockLeagues }),
    })

    const { result } = renderHook(() => useLeagues())

    expect(result.current.loading).toBe(true)
    expect(result.current.leagues).toEqual([])

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.leagues).toEqual(mockLeagues)
    expect(global.fetch).toHaveBeenCalledWith(api.leagues, { cache: 'no-cache' })
    expect(global.fetch).toHaveBeenCalledTimes(1)
  })

  it('should handle network fetch error gracefully by logging error and keeping empty leagues array', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useLeagues())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.leagues).toEqual([])
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching leagues:', expect.objectContaining({
      message: 'Network error'
    }))
    expect(global.fetch).toHaveBeenCalledTimes(1)
    consoleErrorSpy.mockRestore()
  })

  it('should handle non-ok HTTP response (500) by logging error and keeping empty leagues array', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    })

    const { result } = renderHook(() => useLeagues())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.leagues).toEqual([])
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching leagues:', expect.objectContaining({
      message: 'Failed to fetch leagues'
    }))
    expect(global.fetch).toHaveBeenCalledTimes(1)
    consoleErrorSpy.mockRestore()
  })
})
