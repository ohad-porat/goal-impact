'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '../lib/api'
import { SearchResult, SearchResultType } from '../lib/types/search'

const typeToPath: Record<SearchResultType, string> = {
  Player: '/players',
  Club: '/clubs',
  Competition: '/leagues',
  Nation: '/nations',
}

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      setIsOpen(false)
      return
    }

    const timeoutId = setTimeout(async () => {
      setIsLoading(true)
      try {
        const response = await fetch(api.search(query))
        if (!response.ok) {
          throw new Error('Search failed')
        }
        const data = await response.json()
        setResults(data.results || [])
        setIsOpen(data.results && data.results.length > 0)
      } catch (error) {
        console.error('Search error:', error)
        setResults([])
        setIsOpen(false)
      } finally {
        setIsLoading(false)
      }
    }, 300)

    return () => clearTimeout(timeoutId)
  }, [query])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleResultClick = (result: SearchResult) => {
    const path = `${typeToPath[result.type]}/${result.id}`
    setQuery('')
    setIsOpen(false)
    router.push(path)
  }

  return (
    <div ref={searchRef} className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => {
          if (results.length > 0) {
            setIsOpen(true)
          }
        }}
        placeholder="Search..."
        className="px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent w-64"
      />
      
      {isOpen && (
        <div className="absolute top-full mt-1 w-64 bg-slate-700 border border-slate-600 rounded-md shadow-lg z-50 max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="px-4 py-2 text-white">Searching...</div>
          ) : results.length > 0 ? (
            <div className="py-1">
              {results.map((result) => (
                <button
                  key={`${result.type}-${result.id}`}
                  onClick={() => handleResultClick(result)}
                  className="w-full text-left px-4 py-2 hover:bg-slate-600 text-white transition-colors"
                >
                  <div className="flex justify-between items-center gap-4">
                    <span className="font-medium flex-1 truncate">{result.name}</span>
                    <span className="text-sm text-gray-300 flex-shrink-0">{result.type}</span>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="px-4 py-2 text-gray-400">No results found</div>
          )}
        </div>
      )}
    </div>
  )
}
