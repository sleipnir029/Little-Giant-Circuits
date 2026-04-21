// Placeholder — Step C will wire raycast selection to the zustand store here.
export function makeComponentId(type: string, layerIndex?: number): string {
  if (layerIndex !== undefined) return `${type}-${layerIndex}`
  return type
}
