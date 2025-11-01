import { tableStyles } from '../tableStyles'

interface StatCellProps {
  value: number | string | null
  formatter?: (val: number) => string
  className?: string
  style?: 'statsTable' | 'compact'
  textStyle?: 'center' | 'primary' | 'secondary' | 'points'
}

export function StatCell({ 
  value, 
  formatter, 
  className = '', 
  style = 'statsTable',
  textStyle = 'center'
}: StatCellProps) {
  const styleConfig = style === 'statsTable' ? tableStyles.statsTable : tableStyles.compact

  let textConfig: string
  if (style === 'compact' && textStyle === 'points') {
    textConfig = tableStyles.compact.text.points
  } else if (style === 'compact' && textStyle === 'primary') {
    textConfig = tableStyles.compact.text.primary
  } else if (style === 'compact' && textStyle === 'secondary') {
    textConfig = tableStyles.compact.text.secondary
  } else {
    textConfig = styleConfig.text.center
  }

  const displayValue = value !== null 
    ? (typeof value === 'number' && formatter ? formatter(value) : value)
    : '-'

  return (
    <td className={className ? `${styleConfig.cell} ${className}` : styleConfig.cell}>
      <span className={textConfig}>
        {displayValue}
      </span>
    </td>
  )
}
