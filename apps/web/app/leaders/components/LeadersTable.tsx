import { ReactNode } from 'react'
import { ErrorDisplay } from '../../../components/ErrorDisplay'

interface LeadersTableProps {
  title: string
  header: ReactNode
  body: ReactNode
  error?: string | null
  isEmpty?: boolean
}

export function LeadersTable({
  title,
  header,
  body,
  error = null,
  isEmpty = false,
}: LeadersTableProps) {
  if (error) {
    return <ErrorDisplay message={error} />
  }

  if (isEmpty) {
    return (
      <div className="text-white text-center">
        <p>No data available</p>
      </div>
    )
  }

  return (
    <div>
      {title && <h2 className="text-2xl font-bold text-white mb-4">{title}</h2>}
      <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            {header}
            {body}
          </table>
        </div>
      </div>
    </div>
  )
}
