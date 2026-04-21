import type { AttentionGridData } from '../../types'
import { HeatmapGrid } from './HeatmapGrid'

export function AttentionGridViz({ data }: { data: AttentionGridData }) {
  const { layer, n_heads, token_labels, patterns } = data

  // Show up to 4 heads in a 2×2 grid
  const headsToShow = Math.min(n_heads, 4)
  const cols = headsToShow > 2 ? 2 : headsToShow

  // Clamp cell size for large sequences
  const T = token_labels.length
  const cellSize = T > 10 ? 20 : 28

  return (
    <div>
      <p style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
        Layer {layer} attention patterns. Each mini-heatmap shows one attention head.
        <br />
        <strong>Row = "attending FROM" (query)</strong>, <strong>Column = "attending TO" (key)</strong>.
        Darker = more attention weight.
      </p>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${cols}, auto)`,
          gap: 16,
          justifyContent: 'start',
        }}
      >
        {patterns.slice(0, headsToShow).map((pattern, hi) => (
          <div key={hi} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div
              style={{
                fontSize: 11,
                color: '#4f6ef7',
                fontWeight: 600,
                marginBottom: 4,
                background: '#eef1fe',
                padding: '2px 8px',
                borderRadius: 4,
              }}
            >
              Head {hi}
            </div>
            <HeatmapGrid
              data={pattern}
              rowLabels={token_labels}
              colLabels={token_labels}
              colormap="sequential"
              cellSize={cellSize}
              caption={`row attends to column`}
            />
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8, fontSize: 11, color: '#9BA8C0' }}>
        Values are post-softmax attention weights. Each row sums to 1.
      </div>
    </div>
  )
}
