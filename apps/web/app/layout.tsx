import type { Metadata } from 'next'
import { Poppins } from 'next/font/google'
import './globals.css'
import Navbar from '../components/Navbar'

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap',
  variable: '--font-poppins',
})

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
    <html lang="en" className={poppins.variable}>
      <body className={`${poppins.className} bg-slate-900`}>
        <Navbar />
        <main className="pt-12 pb-12">
          {children}
        </main>
      </body>
    </html>
  )
}
