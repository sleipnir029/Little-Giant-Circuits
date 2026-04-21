import type { LogitLensData } from '../../types'
import { HeatmapGrid } from './HeatmapGrid'
import { BarChart } from './BarChart'

export function LogitLensViz({ data }: { data: LogitLensData }) {
  const { layer_labels, token_labels, actual_next_labels, prob_of_actual_next, top_k_final } = data

  const T = token_labels.length
  const cellSize = T > 10 ? 20 : 28

  // prob_of_actual_next: [n_layers][T] — each cell = P(correct next token) at that layer and position
  // We render as a heatmap: rows=layers, cols=positions

  return (
    <div>
      <p style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
        The logit lens asks: "if we forced the model to predict now, at each layer, how
        confident would it be?" Each row is one layer; each column is one token position.
        Color = probability the model assigns to the <em>actual</em> next token.
      </p>

      {/* P(correct) heatmap */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#4a5568', marginBottom: 6 }}>
          P(correct next token) — brighter = more confident
        </div>
        <HeatmapGrid
          data={prob_of_actual_next}
          rowLabels={layer_labels}
          colLabels={token_labels}
          colormap="sequential"
          cellSize={cellSize}
          caption="rows = layers, cols = positions"
        />
        <div style={{ fontSize: 10, color: '#9BA8C0', marginTop: 4 }}>
          Actual next tokens: [{actual_next_labels.join(', ')}]
        </div>
      </div>

      {/* Final layer top-k predictions */}
      <div style={{ marginTop: 8 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#4a5568', marginBottom: 6 }}>
          Final layer top-{top_k_final.k} predictions at position {top_k_final.position}
        </div>
        <BarChart
          values={top_k_final.probs}
          labels={top_k_final.token_labels.map((l) => `token "${l}"`)}
          maxWidth={200}
          barHeight={22}
        />
        <div style={{ fontSize: 10, color: '#9BA8C0', marginTop: 4 }}>
          The model's confidence distribution for the next token at the last informative position.
        </div>
      </div>
    </div>
  )
}
