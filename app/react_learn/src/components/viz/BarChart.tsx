// Shared SVG bar chart primitive — horizontal bars, labeled.
interface BarChartProps {
  values: number[]
  labels: string[]
  colors?: string[]
  maxWidth?: number
  barHeight?: number
  showValues?: boolean
}

const DEFAULT_COLORS = ['#4f6ef7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export function BarChart({
  values,
  labels,
  colors,
  maxWidth = 220,
  barHeight = 20,
  showValues = true,
}: BarChartProps) {
  if (!values.length) return null

  const maxVal = Math.max(...values.map(Math.abs)) || 1
  const labelW = 80
  const valueW = 40
  const gap = 4
  const svgW = labelW + maxWidth + valueW + 8
  const svgH = values.length * (barHeight + gap) + 4

  return (
    <svg width={svgW} height={svgH} style={{ display: 'block' }}>
      {values.map((v, i) => {
        const barW = Math.max(2, (Math.abs(v) / maxVal) * maxWidth)
        const fill = colors?.[i] ?? DEFAULT_COLORS[i % DEFAULT_COLORS.length]
        const y = i * (barHeight + gap) + 2
        return (
          <g key={i}>
            <text
              x={labelW - 4}
              y={y + barHeight / 2 + 4}
              textAnchor="end"
              fontSize={11}
              fill="#4a5568"
            >
              {labels[i]}
            </text>
            <rect x={labelW} y={y} width={barW} height={barHeight} fill={fill} rx={3} opacity={0.85} />
            {showValues && (
              <text
                x={labelW + barW + 4}
                y={y + barHeight / 2 + 4}
                fontSize={10}
                fill="#718096"
              >
                {v.toFixed(3)}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}

// Grouped bar chart — multiple series per position
interface GroupedBarChartProps {
  positions: number[]
  positionLabels: string[]
  series: { name: string; values: number[]; color: string }[]
  barWidth?: number
  maxBarH?: number
  height?: number
}

export function GroupedBarChart({
  positionLabels,
  series,
  barWidth = 12,
  maxBarH = 80,
  height = 120,
}: GroupedBarChartProps) {
  if (!series.length || !positionLabels.length) return null

  const allVals = series.flatMap((s) => s.values)
  const maxVal = Math.max(...allVals) || 1
  const n = positionLabels.length
  const groupW = series.length * (barWidth + 2) + 8
  const labelH = 28
  const legendH = 20
  const svgW = n * groupW + 20
  const svgH = height + labelH + legendH

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg width={svgW} height={svgH} style={{ display: 'block' }}>
        {positionLabels.map((label, pi) => {
          const groupX = pi * groupW + 10
          return (
            <g key={pi}>
              {series.map((s, si) => {
                const barH = Math.max(2, (s.values[pi] / maxVal) * maxBarH)
                const bx = groupX + si * (barWidth + 2)
                const by = height - barH
                return (
                  <rect
                    key={si}
                    x={bx}
                    y={by}
                    width={barWidth}
                    height={barH}
                    fill={s.color}
                    rx={2}
                    opacity={0.85}
                  />
                )
              })}
              <text
                x={groupX + (series.length * (barWidth + 2)) / 2}
                y={height + 14}
                textAnchor="middle"
                fontSize={10}
                fill="#718096"
              >
                {label}
              </text>
            </g>
          )
        })}
        {/* legend */}
        {series.map((s, si) => (
          <g key={si}>
            <rect x={si * 70 + 10} y={svgH - legendH + 4} width={10} height={10} fill={s.color} rx={2} />
            <text x={si * 70 + 24} y={svgH - legendH + 13} fontSize={10} fill="#718096">
              {s.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}
