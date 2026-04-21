// Scene geometry constants — Y=up, computation flows bottom to top
export const TOKEN_SPACING = 0.6    // X gap between residual bus pipes
export const LAYER_SPACING = 3.2    // Y distance between layer module centres
export const LAYER_HEIGHT = 2.4     // total Y extent of one LayerModule box
export const LAYER_DEPTH = 1.0      // Z depth of layer boxes (gives 3D mass)
export const LAYER_WIDTH_BASE = 2.0 // X width added on top of token span
export const SUBBLOCK_HEIGHT = 0.95 // Y height of Attn / MLP inner boxes
export const PLATE_HEIGHT = 0.2     // Y thickness of embed / unembed plates
export const BUS_RADIUS = 0.07      // radius of each residual-stream pipe

// Y position of a layer's centre (layer index 0-based)
export function layerY(i: number): number {
  return 1.8 + i * LAYER_SPACING
}

// Y position of the unembed plate centre
export function unembedY(nLayers: number): number {
  return layerY(nLayers - 1) + LAYER_SPACING * 0.7
}

// Bottom / top Y of residual bus (extends slightly past embed + unembed)
export function busBottomY(): number {
  return -PLATE_HEIGHT / 2 - 0.3
}

export function busTopY(nLayers: number): number {
  return unembedY(nLayers) + PLATE_HEIGHT / 2 + 0.3
}

// Total X span of the token array
export function tokenSpan(nTokens: number): number {
  return (nTokens - 1) * TOKEN_SPACING
}

// X position of token i (centred on 0)
export function tokenX(i: number, nTokens: number): number {
  return i * TOKEN_SPACING - tokenSpan(nTokens) / 2
}

// Scene mid-height (for camera framing)
export function sceneMidY(nLayers: number): number {
  return (busBottomY() + busTopY(nLayers)) / 2
}
