import { tokenSpan, LAYER_HEIGHT, LAYER_DEPTH, SUBBLOCK_HEIGHT } from '../logic/sceneConfig'
import { AttentionBlock } from './AttentionBlock'
import { MlpBlock } from './MlpBlock'

interface LayerModuleProps {
  layerIndex: number
  nTokens: number
  y: number
}

// Gap between the two inner blocks
const INNER_GAP = 0.1
// attn sits in bottom half, mlp in top half
const ATTN_Y = -(SUBBLOCK_HEIGHT / 2 + INNER_GAP / 2)
const MLP_Y = SUBBLOCK_HEIGHT / 2 + INNER_GAP / 2

export function LayerModule({ layerIndex, nTokens, y }: LayerModuleProps) {
  const width = tokenSpan(nTokens) + 1.2

  return (
    <group position={[0, y, 0]}>
      {/* Outer shell — transparent so inner blocks are visible */}
      <mesh>
        <boxGeometry args={[width, LAYER_HEIGHT, LAYER_DEPTH]} />
        <meshStandardMaterial
          color="#1e2a3a"
          transparent
          opacity={0.25}
          metalness={0.2}
          roughness={0.8}
          wireframe={false}
        />
      </mesh>

      <AttentionBlock layerIndex={layerIndex} width={width} yOffset={ATTN_Y} />
      <MlpBlock layerIndex={layerIndex} width={width} yOffset={MLP_Y} />
    </group>
  )
}
