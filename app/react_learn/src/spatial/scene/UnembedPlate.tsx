import { Html } from '@react-three/drei'
import { useSpatialStore } from '../../hooks/useSpatialStore'
import { tokenSpan, PLATE_HEIGHT, LAYER_DEPTH } from '../logic/sceneConfig'
import { makeComponentId } from '../logic/selection'

interface UnembedPlateProps {
  nTokens: number
  y: number
}

const ID = makeComponentId('unembed')
const COLOR_BASE = '#7c3aed'
const COLOR_HOVER = '#8b5cf6'
const COLOR_SELECTED = '#c4b5fd'

export function UnembedPlate({ nTokens, y }: UnembedPlateProps) {
  const { selectedId, hoveredId, setSelected, setHovered } = useSpatialStore()
  const isSelected = selectedId === ID
  const isHovered = hoveredId === ID

  const width = tokenSpan(nTokens) + 1.2
  const color = isSelected ? COLOR_SELECTED : isHovered ? COLOR_HOVER : COLOR_BASE

  return (
    <group position={[0, y, 0]}>
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
        <span style={{ fontSize: 11, fontWeight: 700, color: '#c4b5fd', whiteSpace: 'nowrap', textShadow: '0 1px 3px #000' }}>
          Unembed
        </span>
      </Html>
    </group>
  )
}
