import type { VizPayload, TokensData, EmbedNormsData, AttentionGridData, MlpHeatmapData, ResidNormsData, LogitLensData } from '../types'
import { TokensViz } from './viz/TokensViz'
import { EmbedNormsViz } from './viz/EmbedNormsViz'
import { AttentionGridViz } from './viz/AttentionGridViz'
import { MlpHeatmapViz } from './viz/MlpHeatmapViz'
import { ResidNormsViz } from './viz/ResidNormsViz'
import { LogitLensViz } from './viz/LogitLensViz'

export function StageViz({ viz }: { viz: VizPayload }) {
  switch (viz.kind) {
    case 'tokens':
      return <TokensViz data={viz.data as TokensData} />
    case 'embed_norms':
      return <EmbedNormsViz data={viz.data as EmbedNormsData} />
    case 'attention_grid':
      return <AttentionGridViz data={viz.data as AttentionGridData} />
    case 'mlp_heatmap':
      return <MlpHeatmapViz data={viz.data as MlpHeatmapData} />
    case 'resid_norms':
      return <ResidNormsViz data={viz.data as ResidNormsData} />
    case 'logit_lens':
      return <LogitLensViz data={viz.data as LogitLensData} />
    default:
      return (
        <div style={{ color: '#ef4444', padding: 16 }}>
          Unknown viz kind: {(viz as VizPayload).kind}
        </div>
      )
  }
}
