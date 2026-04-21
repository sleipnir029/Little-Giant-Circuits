import type { MlpHeatmapData } from '../../types'
import { HeatmapGrid } from './HeatmapGrid'

export function MlpHeatmapViz({ data }: { data: MlpHeatmapData }) {
  const { layer, token_labels, top_neuron_indices, activations } = data

  // activations shape: [T][k] — we want [k][T] for rows=neurons, cols=positions
  const k = top_neuron_indices.length
  const T = token_labels.length
  const transposed: number[][] = Array.from({ length: k }, (_, ni) =>
    Array.from({ length: T }, (_, ti) => activations[ti][ni])
  )

  // Clamp cell size for wide sequences or many neurons
  const cellSize = T > 10 ? 18 : T > 5 ? 22 : 28
  const neuronLabels = top_neuron_indices.map((idx) => `n${idx}`)

  // Show only top 20 neurons to keep the grid manageable in the layout
  const maxNeurons = 20
  const displayData = transposed.slice(0, maxNeurons)
  const displayLabels = neuronLabels.slice(0, maxNeurons)

  return (
    <div>
      <p style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
        Layer {layer} MLP activations (post-GELU). Rows are the top-{Math.min(k, maxNeurons)} most
        active neurons; columns are token positions. Red = positive activation, blue = negative.
      </p>
      <HeatmapGrid
        data={displayData}
        rowLabels={displayLabels}
        colLabels={token_labels}
        colormap="diverging"
        cellSize={cellSize}
      />
      <div style={{ marginTop: 8, fontSize: 11, color: '#9BA8C0' }}>
        Neurons selected by max absolute activation across positions. Diverging colormap: red = positive, blue = negative, white = zero.
      </div>
    </div>
  )
}
