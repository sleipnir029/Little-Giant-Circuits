// Types matching the Phase 3B JSON contract exactly.
// Source of truth: docs/architecture/react_learn_mode.md §5

export interface TokensData {
  positions: number[]
  tokens: number[]
  token_labels: string[]
}

export interface EmbedNormsData {
  positions: number[]
  token_labels: string[]
  tok_norms: number[]
  pos_norms: number[]
  combined_norms: number[]
}

export interface AttentionGridData {
  layer: number
  n_heads: number
  token_labels: string[]
  patterns: number[][][] // [H][T][T]
}

export interface MlpHeatmapData {
  layer: number
  token_labels: string[]
  top_neuron_indices: number[] // [k]
  activations: number[][] // [T][k]
}

export interface ResidNormsData {
  highlight_layer: number | null
  token_labels: string[]
  stage_names: string[]
  norms: Record<string, number[]> // {stage_name: float[T]}
}

export interface LogitLensData {
  layer_labels: string[]
  token_labels: string[]
  actual_nexts: number[]
  actual_next_labels: string[]
  prob_of_actual_next: number[][] // [n_layers][T]
  top_k_final: {
    position: number
    k: number
    token_ids: number[]
    token_labels: string[]
    probs: number[]
  }
}

export type VizKind =
  | 'tokens'
  | 'embed_norms'
  | 'attention_grid'
  | 'mlp_heatmap'
  | 'resid_norms'
  | 'logit_lens'

export type VizData =
  | TokensData
  | EmbedNormsData
  | AttentionGridData
  | MlpHeatmapData
  | ResidNormsData
  | LogitLensData

export interface VizPayload {
  kind: VizKind
  data: VizData
}

export interface Stage {
  index: number
  name: string
  explanation: string
  what_changed: string
  what_to_notice: string
  next_technical_view: string
  viz: VizPayload
}

export interface LearnPackage {
  task: string
  trace_id: string
  n_tokens: number
  n_layers: number
  n_heads: number
  d_model: number
  vocab_size: number
  token_labels: string[]
  stages: Stage[]
}

export interface ManifestEntry {
  task: string
  trace_id: string
  path: string
  n_tokens: number
  n_layers: number
  n_stages: number
}

export interface Manifest {
  generated_at: string
  packages: ManifestEntry[]
}
