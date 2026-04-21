import { Html } from '@react-three/drei'
import { useSpatialStore } from '../../hooks/useSpatialStore'
import { SUBBLOCK_HEIGHT, LAYER_DEPTH } from '../logic/sceneConfig'
import { makeComponentId } from '../logic/selection'

interface AttentionBlockProps {
  layerIndex: number
  width: number
  yOffset: number
}

const COLOR_BASE = '#1e40af'
const COLOR_HOVER = '#2563eb'
const COLOR_SELECTED = '#60a5fa'

export function AttentionBlock({ layerIndex, width, yOffset }: AttentionBlockProps) {
  const id = makeComponentId('attn', layerIndex)
  const { selectedId, hoveredId, setSelected, setHovered } = useSpatialStore()
  const isSelected = selectedId === id
  const isHovered = hoveredId === id

  const color = isSelected ? COLOR_SELECTED : isHovered ? COLOR_HOVER : COLOR_BASE

  return (
    <group position={[0, yOffset, 0]}>
      <mesh
        onClick={(e) => { e.stopPropagation(); setSelected(isSelected ? null : id) }}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(id) }}
        onPointerOut={() => setHovered(null)}
      >
        <boxGeometry args={[width - 0.2, SUBBLOCK_HEIGHT, LAYER_DEPTH - 0.1]} />
        <meshStandardMaterial color={color} metalness={0.4} roughness={0.5} />
      </mesh>
      <Html
        position={[0, SUBBLOCK_HEIGHT / 2 + 0.08, 0]}
        center
        style={{ pointerEvents: 'none' }}
      >
        <span style={{ fontSize: 10, fontWeight: 600, color: '#93c5fd', whiteSpace: 'nowrap', textShadow: '0 1px 3px #000' }}>
          Layer {layerIndex} · Attention
        </span>
      </Html>
    </group>
  )
}
