import type { EmbedNormsData } from '../../types'
import { GroupedBarChart } from './BarChart'

export function EmbedNormsViz({ data }: { data: EmbedNormsData }) {
  const series = [
    { name: 'token', values: data.tok_norms, color: '#4f6ef7' },
    { name: 'position', values: data.pos_norms, color: '#10b981' },
    { name: 'combined', values: data.combined_norms, color: '#f59e0b' },
  ]

  return (
    <div>
      <p style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
        Each group shows the L2 norm (vector magnitude) of the three embedding components at that
        token position. Taller bars = larger vectors = more "energy" in the stream.
      </p>
      <GroupedBarChart
        positions={data.positions}
        positionLabels={data.token_labels}
        series={series}
        barWidth={14}
        maxBarH={90}
        height={110}
      />
      <div style={{ marginTop: 8, fontSize: 11, color: '#9BA8C0' }}>
        x-axis: token positions · y-axis: L2 norm magnitude
      </div>
    </div>
  )
}
