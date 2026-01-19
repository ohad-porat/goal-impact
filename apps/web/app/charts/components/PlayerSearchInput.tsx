"use client";

import { useState, useEffect, useRef } from "react";
import { api } from "../../../lib/api";
import { SearchResult } from "../../../lib/types/search";

interface PlayerSearchInputProps {
  label: string;
  onPlayerSelect: (player: SearchResult | null) => void;
  selectedPlayer: SearchResult | null;
}

export function PlayerSearchInput({
  label,
  onPlayerSelect,
  selectedPlayer,
}: PlayerSearchInputProps) {
  const [query, setQuery] = useState(selectedPlayer?.name || "");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selectedPlayer) {
      setQuery(selectedPlayer.name);
    } else {
      setQuery("");
    }
  }, [selectedPlayer]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsOpen(false);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setIsOpen(true);

    const timeoutId = setTimeout(async () => {
      try {
        const response = await fetch(api.search(query, "Player"));
        if (!response.ok) {
          throw new Error("Search failed");
        }
        const data = await response.json();
        setResults(data.results || []);
        setIsOpen(true);
      } catch (error) {
        console.error("Search error:", error);
        setResults([]);
        setIsOpen(false);
      } finally {
        setIsLoading(false);
      }
    }, 400);

    return () => clearTimeout(timeoutId);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleResultClick = (result: SearchResult) => {
    onPlayerSelect(result);
    setQuery(result.name);
    setIsOpen(false);
  };

  const handleClear = () => {
    onPlayerSelect(null);
    setQuery("");
    setIsOpen(false);
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        {label}
      </label>
      <div ref={searchRef} className="relative">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              if (results.length > 0 || isLoading || query.trim()) {
                setIsOpen(true);
              }
            }}
            placeholder="Search for a player..."
            className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-md border border-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
          />
          {selectedPlayer && (
            <button
              onClick={handleClear}
              className="px-4 py-2 bg-slate-600 text-white rounded-md border border-slate-600 hover:bg-slate-500 transition-colors"
            >
              Clear
            </button>
          )}
        </div>

        {isOpen && (
          <div className="absolute top-full mt-1 w-full bg-slate-700 border border-slate-600 rounded-md shadow-lg z-50 max-h-96 overflow-y-auto">
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
                      <span className="font-medium flex-1 truncate">
                        {result.name}
                      </span>
                      <span className="text-sm text-gray-300 shrink-0">
                        {result.type}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="px-4 py-2 text-gray-400">No players found</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
