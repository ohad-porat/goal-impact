import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navbar from '../components/Navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Goal Impact - Soccer Analytics',
  description: 'Advanced soccer data analytics with Goal Value and Points Added metrics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-900`}>
        <Navbar />
        <main className="pt-12">
          {children}
        </main>
      </body>
    </html>
  )
}
