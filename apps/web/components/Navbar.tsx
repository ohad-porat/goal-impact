"use client";

import { useState } from "react";
import Link from "next/link";
import SearchBar from "./SearchBar";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const linkClasses =
    "text-black font-semibold text-base sm:text-lg uppercase tracking-wide hover:text-slate-700 transition-colors";
  const logoClasses =
    "text-black font-bold text-xl sm:text-2xl uppercase tracking-wide hover:text-slate-700 transition-colors";

  return (
    <nav className="bg-orange-400 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4 sm:space-x-8">
            <Link href="/" className={`${logoClasses} mr-2 sm:mr-6`}>
              GOAL IMPACT
            </Link>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/leaders" className={linkClasses}>
                Leaders
              </Link>
              <Link href="/charts" className={linkClasses}>
                Charts
              </Link>
              <Link href="/nations" className={linkClasses}>
                Nations
              </Link>
              <Link href="/leagues" className={linkClasses}>
                Leagues
              </Link>
              <Link href="/clubs" className={linkClasses}>
                Clubs
              </Link>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <div className="hidden sm:block">
              <SearchBar />
            </div>

            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-black hover:text-slate-700 transition-colors"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-orange-500 py-4 space-y-4">
            <div className="sm:hidden mb-4">
              <SearchBar />
            </div>
            <Link
              href="/leaders"
              className={`${linkClasses} block`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Leaders
            </Link>
            <Link
              href="/charts"
              className={`${linkClasses} block`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Charts
            </Link>
            <Link
              href="/nations"
              className={`${linkClasses} block`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Nations
            </Link>
            <Link
              href="/leagues"
              className={`${linkClasses} block`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Leagues
            </Link>
            <Link
              href="/clubs"
              className={`${linkClasses} block`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Clubs
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
