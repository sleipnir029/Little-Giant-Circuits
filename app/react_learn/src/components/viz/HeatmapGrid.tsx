// Shared SVG heatmap primitive.
// Supports two colormaps: 'sequential' (white→blue) and 'diverging' (blue→white→red).

interface HeatmapGridProps {
  data: number[][] // [rows][cols]
  rowLabels?: string[]
  colLabels?: string[]
  colormap?: 'sequential' | 'diverging'
  cellSize?: number
  showValues?: boolean
  caption?: string
}

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t
}

function sequentialColor(v: number): string {
  // white (0) → indigo (1)
  const r = Math.round(lerp(240, 55, v))
  const g = Math.round(lerp(243, 90, v))
  const b = Math.round(lerp(255, 230, v))
  return `rgb(${r},${g},${b})`
}

function divergingColor(v: number): string {
  // blue (-1) → white (0) → red (+1)  — v is already normalized to [-1,1]
  if (v < 0) {
    const t = -v
    const r = Math.round(lerp(255, 55, t))
    const g = Math.round(lerp(255, 100, t))
    const b = Math.round(lerp(255, 230, t))
    return `rgb(${r},${g},${b})`
  } else {
    const t = v
    const r = Math.round(lerp(255, 220, t))
    const g = Math.round(lerp(255, 50, t))
    const b = Math.round(lerp(255, 50, t))
    return `rgb(${r},${g},${b})`
  }
}

export function HeatmapGrid({
  data,
  rowLabels,
  colLabels,
  colormap = 'sequential',
  cellSize = 28,
  showValues = false,
  caption,
}: HeatmapGridProps) {
  if (!data.length || !data[0].length) return null

  const nRows = data.length
  const nCols = data[0].length

  // normalise values for coloring
  const flat = data.flat()
  const vMin = Math.min(...flat)
  const vMax = Math.max(...flat)
  const vRange = vMax - vMin || 1

  function cellColor(v: number): string {
    if (colormap === 'diverging') {
      const absMax = Math.max(Math.abs(vMin), Math.abs(vMax)) || 1
      return divergingColor(v / absMax)
    }
    return sequentialColor((v - vMin) / vRange)
  }

  const labelPad = rowLabels ? 42 : 4
  const colLabelH = colLabels ? 38 : 4
  const svgW = labelPad + nCols * cellSize + 4
  const svgH = colLabelH + nRows * cellSize + (caption ? 20 : 4)

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg width={svgW} height={svgH} style={{ display: 'block' }}>
        {/* column labels */}
        {colLabels &&
          colLabels.map((label, ci) => (
            <text
              key={ci}
              x={labelPad + ci * cellSize + cellSize / 2}
              y={colLabelH - 6}
              textAnchor="middle"
              fontSize={10}
              fill="#718096"
              transform={`rotate(-40, ${labelPad + ci * cellSize + cellSize / 2}, ${colLabelH - 6})`}
            >
              {label}
            </text>
          ))}
        {/* row labels */}
        {rowLabels &&
          rowLabels.map((label, ri) => (
            <text
              key={ri}
              x={labelPad - 4}
              y={colLabelH + ri * cellSize + cellSize / 2 + 4}
              textAnchor="end"
              fontSize={10}
              fill="#718096"
            >
              {label}
            </text>
          ))}
        {/* cells */}
        {data.map((row, ri) =>
          row.map((val, ci) => (
            <g key={`${ri}-${ci}`}>
              <rect
                x={labelPad + ci * cellSize}
                y={colLabelH + ri * cellSize}
                width={cellSize - 1}
                height={cellSize - 1}
                fill={cellColor(val)}
                rx={2}
              />
              {showValues && cellSize >= 32 && (
                <text
                  x={labelPad + ci * cellSize + cellSize / 2}
                  y={colLabelH + ri * cellSize + cellSize / 2 + 4}
                  textAnchor="middle"
                  fontSize={8}
                  fill={val > (vMin + vRange * 0.6) ? '#fff' : '#333'}
                >
                  {val.toFixed(2)}
                </text>
              )}
            </g>
          ))
        )}
        {/* caption */}
        {caption && (
          <text
            x={svgW / 2}
            y={svgH - 4}
            textAnchor="middle"
            fontSize={10}
            fill="#9BA8C0"
            fontStyle="italic"
          >
            {caption}
          </text>
        )}
      </svg>
    </div>
  )
}
