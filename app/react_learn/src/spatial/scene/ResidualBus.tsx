import { tokenX, busBottomY, busTopY } from '../logic/sceneConfig'

interface ResidualBusProps {
  nTokens: number
  nLayers: number
}

export function ResidualBus({ nTokens, nLayers }: ResidualBusProps) {
  const bottom = busBottomY()
  const top = busTopY(nLayers)
  const height = top - bottom
  const midY = bottom + height / 2

  return (
    <group>
      {Array.from({ length: nTokens }, (_, i) => {
        const x = tokenX(i, nTokens)
        return (
          <mesh key={i} position={[x, midY, 0]}>
            {/* CylinderGeometry: radiusTop, radiusBottom, height, radialSegments */}
            <cylinderGeometry args={[0.07, 0.07, height, 12]} />
            <meshStandardMaterial
              color="#7eb0f5"
              transparent
              opacity={0.35}
              metalness={0.1}
              roughness={0.7}
            />
          </mesh>
        )
      })}
    </group>
  )
}
