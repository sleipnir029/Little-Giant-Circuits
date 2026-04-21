import type { ResidNormsData } from '../../types'

const LINE_COLORS = ['#4f6ef7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']

export function ResidNormsViz({ data }: { data: ResidNormsData }) {
  const { token_labels, stage_names, norms, highlight_layer } = data

  const T = token_labels.length
  const allVals = stage_names.flatMap((s) => norms[s] ?? [])
  const maxVal = Math.max(...allVals) || 1

  const W = 340
  const H = 160
  const padL = 48
  const padB = 32
  const padT = 12
  const plotW = W - padL
  const plotH = H - padB - padT

  function xOf(i: number) {
    if (T === 1) return padL + plotW / 2
    return padL + (i / (T - 1)) * plotW
  }
  function yOf(v: number) {
    return padT + plotH - (v / maxVal) * plotH
  }

  return (
    <div>
      <p style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
        Residual stream L2 norms at each token position, measured at different points in the forward
        pass. Each line is one stage. Growing norms = more information being written to the stream.
        {highlight_layer !== null && (
          <> Layer {highlight_layer} stages are highlighted.</>
        )}
      </p>
      <div style={{ overflowX: 'auto' }}>
        <svg width={W} height={H} style={{ display: 'block' }}>
          {/* y-axis ticks */}
          {[0, 0.25, 0.5, 0.75, 1].map((frac) => {
            const y = yOf(frac * maxVal)
            return (
              <g key={frac}>
                <line x1={padL - 4} x2={padL} y1={y} y2={y} stroke="#e2e8f0" />
                <text x={padL - 6} y={y + 4} textAnchor="end" fontSize={9} fill="#9BA8C0">
                  {(frac * maxVal).toFixed(1)}
                </text>
              </g>
            )
          })}
          {/* x-axis labels */}
          {token_labels.map((label, i) => (
            <text
              key={i}
              x={xOf(i)}
              y={H - 4}
              textAnchor="middle"
              fontSize={10}
              fill="#718096"
            >
              {label}
            </text>
          ))}
          {/* lines */}
          {stage_names.map((sname, si) => {
            const vals = norms[sname] ?? []
            if (!vals.length) return null
            const color = LINE_COLORS[si % LINE_COLORS.length]
            const opacity = highlight_layer !== null && !sname.startsWith(`L${highlight_layer}`) && sname !== 'embed' ? 0.25 : 1
            const points = vals.map((v, i) => `${xOf(i)},${yOf(v)}`).join(' ')
            return (
              <g key={sname} opacity={opacity}>
                <polyline points={points} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" />
                {vals.map((v, i) => (
                  <circle key={i} cx={xOf(i)} cy={yOf(v)} r={3} fill={color} />
                ))}
              </g>
            )
          })}
          {/* axis lines */}
          <line x1={padL} x2={W - 4} y1={padT + plotH} y2={padT + plotH} stroke="#cbd5e0" />
          <line x1={padL} x2={padL} y1={padT} y2={padT + plotH} stroke="#cbd5e0" />
        </svg>
      </div>
      {/* legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 12px', marginTop: 8 }}>
        {stage_names.map((sname, si) => (
          <div key={sname} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: '#718096' }}>
            <div
              style={{
                width: 16,
                height: 3,
                background: LINE_COLORS[si % LINE_COLORS.length],
                borderRadius: 2,
              }}
            />
            {sname}
          </div>
        ))}
      </div>
    </div>
  )
}
