import Link from 'next/link'

export default function Navbar() {
  const linkClasses = "text-black font-semibold text-md uppercase tracking-wide hover:text-slate-700 transition-colors"
  const logoClasses = "text-black font-bold text-xl uppercase tracking-wide hover:text-slate-700 transition-colors"

  return (
    <nav className="bg-orange-400 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className={logoClasses}>
            GOAL IMPACT
          </Link>
          
          <div className="flex space-x-8">
            <Link href="/nations" className={linkClasses}>
              Nations
            </Link>
            <Link href="/leagues" className={linkClasses}>
              Leagues
            </Link>
            <Link href="/clubs" className={linkClasses}>
              Clubs
            </Link>
            <Link href="/leaders" className={linkClasses}>
              Leaders
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
