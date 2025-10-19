export const ErrorDisplay = ({ message }: { message: string }) => {
  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="text-red-400 text-xl">Error: {message}</div>
        </div>
      </div>
    </div>
  )
}
