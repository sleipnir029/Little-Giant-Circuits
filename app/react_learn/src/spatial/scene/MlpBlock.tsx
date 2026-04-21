import { Html } from '@react-three/drei'
import { useSpatialStore } from '../../hooks/useSpatialStore'
import { SUBBLOCK_HEIGHT, LAYER_DEPTH } from '../logic/sceneConfig'
import { makeComponentId } from '../logic/selection'

interface MlpBlockProps {
  layerIndex: number
  width: number
  yOffset: number
}

const COLOR_BASE = '#0d6b63'
const COLOR_HOVER = '#0d9488'
const COLOR_SELECTED = '#5eead4'

export function MlpBlock({ layerIndex, width, yOffset }: MlpBlockProps) {
  const id = makeComponentId('mlp', layerIndex)
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
        <span style={{ fontSize: 10, fontWeight: 600, color: '#5eead4', whiteSpace: 'nowrap', textShadow: '0 1px 3px #000' }}>
          Layer {layerIndex} · MLP
        </span>
      </Html>
    </group>
  )
}
