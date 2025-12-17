import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSeasons } from './useSeasons'
import { api } from '../../../lib/api'

vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  useSearchParams: vi.fn(),
}))

vi.mock('../../../lib/api', () => ({
  api: {
    leagueSeasons: (leagueId: number) => `https://api.example.com/leagues/${leagueId}/seasons`,
    allSeasons: 'https://api.example.com/leagues/seasons',
  } as any,
}))

describe('useSeasons', () => {
  const mockPush = vi.fn()
  const mockRouter = {
    push: mockPush,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
    ;(useRouter as any).mockReturnValue(mockRouter)
  })

  it('should fetch all seasons from allSeasons endpoint when leagueId is undefined', async () => {
    const mockSeasons = [
      { id: 1, start_year: 2023, end_year: 2024, display_name: '2023/24' },
      { id: 2, start_year: 2022, end_year: 2023, display_name: '2022/23' },
    ]

    const mockSearchParams = new URLSearchParams('season_id=1')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seasons: mockSeasons }),
    })

    const { result } = renderHook(() => useSeasons())

    expect(result.current.loading).toBe(true)
    expect(result.current.seasons).toEqual([])

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.seasons).toEqual(mockSeasons)
    expect(global.fetch).toHaveBeenCalledWith(api.allSeasons, { cache: 'no-cache' })
    expect(global.fetch).toHaveBeenCalledTimes(1)
  })

  it('should fetch league-specific seasons from leagueSeasons endpoint when leagueId is provided', async () => {
    const mockSeasons = [
      { id: 3, start_year: 2023, end_year: 2024, display_name: '2023/24' },
    ]

    const mockSearchParams = new URLSearchParams('season_id=3')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seasons: mockSeasons }),
    })

    const { result } = renderHook(() => useSeasons(5))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.seasons).toEqual(mockSeasons)
    expect(global.fetch).toHaveBeenCalledWith(api.leagueSeasons(5), { cache: 'no-cache' })
    expect(global.fetch).toHaveBeenCalledTimes(1)
  })

  it('should auto-select most recent season and navigate to URL with season_id and view=season when no season_id is present', async () => {
    const mockSeasons = [
      { id: 1, start_year: 2023, end_year: 2024, display_name: '2023/24' },
      { id: 2, start_year: 2022, end_year: 2023, display_name: '2022/23' },
    ]

    const mockSearchParams = new URLSearchParams()
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seasons: mockSeasons }),
    })

    renderHook(() => useSeasons())

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled()
    })

    const callArgs = mockPush.mock.calls[0][0]
    const url = new URL(`http://localhost${callArgs}`)
    expect(url.searchParams.get('season_id')).toBe('1')
    expect(url.searchParams.get('view')).toBe('season')
  })

  it('should not auto-select or navigate when season_id is already present in URL', async () => {
    const mockSeasons = [
      { id: 1, start_year: 2023, end_year: 2024, display_name: '2023/24' },
      { id: 2, start_year: 2022, end_year: 2023, display_name: '2022/23' },
    ]

    const mockSearchParams = new URLSearchParams('season_id=2')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seasons: mockSeasons }),
    })

    const { result } = renderHook(() => useSeasons())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(mockPush).not.toHaveBeenCalled()
  })

  it('should not auto-select or navigate when seasons array is empty after fetch', async () => {
    const mockSearchParams = new URLSearchParams()
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seasons: [] }),
    })

    const { result } = renderHook(() => useSeasons())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(mockPush).not.toHaveBeenCalled()
  })

  it('should preserve existing view parameter (career) when auto-selecting season', async () => {
    const mockSeasons = [
      { id: 1, start_year: 2023, end_year: 2024, display_name: '2023/24' },
    ]

    const mockSearchParams = new URLSearchParams('view=career')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seasons: mockSeasons }),
    })

    renderHook(() => useSeasons())

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled()
    })

    const callArgs = mockPush.mock.calls[0][0]
    const url = new URL(`http://localhost${callArgs}`)
    expect(url.searchParams.get('view')).toBe('career')
    expect(url.searchParams.get('season_id')).toBe('1')
  })

  it('should refetch when leagueId changes from 5 to 7 and update seasons accordingly', async () => {
    const mockSeasons1 = [{ id: 1, start_year: 2023, end_year: 2024, display_name: '2023/24' }]
    const mockSeasons2 = [{ id: 2, start_year: 2022, end_year: 2023, display_name: '2022/23' }]

    const mockSearchParams = new URLSearchParams('season_id=1')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ seasons: mockSeasons1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ seasons: mockSeasons2 }),
      })

    const { result, rerender } = renderHook(({ leagueId }: { leagueId?: number }) => useSeasons(leagueId), {
      initialProps: { leagueId: 5 },
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.seasons).toEqual(mockSeasons1)
    expect(global.fetch).toHaveBeenCalledWith(api.leagueSeasons(5), { cache: 'no-cache' })

    rerender({ leagueId: 7 })

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.seasons).toEqual(mockSeasons2)
    expect(global.fetch).toHaveBeenCalledWith(api.leagueSeasons(7), { cache: 'no-cache' })
    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it('should handle network fetch error gracefully by logging error and keeping empty seasons array', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const mockSearchParams = new URLSearchParams('season_id=1')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useSeasons())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.seasons).toEqual([])
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching seasons:', expect.objectContaining({
      message: 'Network error'
    }))
    expect(global.fetch).toHaveBeenCalledTimes(1)
    consoleErrorSpy.mockRestore()
  })

  it('should handle non-ok HTTP response (500) by logging error and keeping empty seasons array', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const mockSearchParams = new URLSearchParams('season_id=1')
    ;(useSearchParams as any).mockReturnValue(mockSearchParams)

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    })

    const { result } = renderHook(() => useSeasons())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.seasons).toEqual([])
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching seasons:', expect.objectContaining({
      message: 'Failed to fetch seasons'
    }))
    expect(global.fetch).toHaveBeenCalledTimes(1)
    consoleErrorSpy.mockRestore()
  })
})
