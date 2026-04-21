import { Html } from '@react-three/drei'
import { useSpatialStore } from '../../hooks/useSpatialStore'
import { tokenSpan, PLATE_HEIGHT, LAYER_DEPTH } from '../logic/sceneConfig'
import { makeComponentId } from '../logic/selection'

interface EmbedPlateProps {
  nTokens: number
}

const ID = makeComponentId('embed')
const COLOR_BASE = '#1d4ed8'
const COLOR_HOVER = '#2563eb'
const COLOR_SELECTED = '#60a5fa'

export function EmbedPlate({ nTokens }: EmbedPlateProps) {
  const { selectedId, hoveredId, setSelected, setHovered } = useSpatialStore()
  const isSelected = selectedId === ID
  const isHovered = hoveredId === ID

  const width = tokenSpan(nTokens) + 1.2
  const color = isSelected ? COLOR_SELECTED : isHovered ? COLOR_HOVER : COLOR_BASE

  return (
    <group position={[0, 0, 0]}>
      <mesh
        onClick={(e) => { e.stopPropagation(); setSelected(isSelected ? null : ID) }}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(ID) }}
        onPointerOut={() => setHovered(null)}
      >
        <boxGeometry args={[width, PLATE_HEIGHT, LAYER_DEPTH]} />
        <meshStandardMaterial color={color} metalness={0.3} roughness={0.6} />
      </mesh>
      <Html
        position={[0, PLATE_HEIGHT / 2 + 0.18, 0]}
        center
        style={{ pointerEvents: 'none' }}
      >
        <span style={{ fontSize: 11, fontWeight: 700, color: '#93c5fd', whiteSpace: 'nowrap', textShadow: '0 1px 3px #000' }}>
          Embed
        </span>
      </Html>
    </group>
  )
}
