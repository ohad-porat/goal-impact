import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorDisplay } from './ErrorDisplay'

describe('ErrorDisplay', () => {
  it('should render error message', () => {
    render(<ErrorDisplay message="Test error message" />)
    
    expect(screen.getByText(/Error:/)).toBeInTheDocument()
    expect(screen.getByText(/Test error message/)).toBeInTheDocument()
  })

  it('should display the error message in the correct format', () => {
    render(<ErrorDisplay message="Failed to load data" />)
    
    const errorText = screen.getByText('Error: Failed to load data')
    expect(errorText).toBeInTheDocument()
    expect(errorText).toHaveClass('text-red-400', 'text-xl')
  })

  it('should handle empty error message', () => {
    render(<ErrorDisplay message="" />)
    
    expect(screen.getByText('Error:')).toBeInTheDocument()
  })

  it('should handle long error messages', () => {
    const longMessage = 'This is a very long error message that might wrap to multiple lines and should still be displayed correctly'
    render(<ErrorDisplay message={longMessage} />)
    
    expect(screen.getByText(new RegExp(longMessage))).toBeInTheDocument()
  })

  it('should have correct container structure and classes', () => {
    const { container } = render(<ErrorDisplay message="Test" />)
    
    const mainDiv = container.firstChild as HTMLElement
    expect(mainDiv).toHaveClass('min-h-screen', 'py-8')
    
    const innerDiv = mainDiv.querySelector('.max-w-7xl')
    expect(innerDiv).toBeInTheDocument()
    expect(innerDiv).toHaveClass('mx-auto', 'px-4', 'sm:px-6', 'lg:px-8')
  })
})
