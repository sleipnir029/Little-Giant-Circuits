import { useRef, useEffect } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import type { LearnPackage } from '../types'
import { SceneRoot } from './scene/SceneRoot'
import { sceneMidY } from './logic/sceneConfig'
import { useSpatialStore } from '../hooks/useSpatialStore'

// CameraController lives inside Canvas so it can call useThree().
// It fires whenever resetTick increments, restoring camera to home position.
function CameraController({
  camPos,
  target,
  controlsRef,
}: {
  camPos: [number, number, number]
  target: [number, number, number]
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  controlsRef: React.RefObject<any>
}) {
  const { camera } = useThree()
  const { resetTick } = useSpatialStore()

  useEffect(() => {
    camera.position.set(...camPos)
    if (controlsRef.current) {
      controlsRef.current.target.set(...target)
      controlsRef.current.update()
    }
  // resetTick change is the only signal that should fire this
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetTick])

  return null
}

interface SpatialViewerProps {
  pkg: LearnPackage
}

export function SpatialViewer({ pkg }: SpatialViewerProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const controlsRef = useRef<any>(null)
  const { n_layers, n_tokens } = pkg

  const midY = sceneMidY(n_layers)
  const camZ = 12 + n_tokens * 0.4
  const camPos: [number, number, number] = [0, midY, camZ]
  const target: [number, number, number] = [0, midY, 0]

  const { setSelected, triggerReset } = useSpatialStore()

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <Canvas
        style={{ background: '#0f1117' }}
        gl={{ antialias: true }}
        camera={{ position: camPos, fov: 50, near: 0.1, far: 200 }}
        onPointerMissed={() => setSelected(null)}
      >
        <OrbitControls
          ref={controlsRef}
          enableDamping
          dampingFactor={0.08}
          minDistance={4}
          maxDistance={40}
          maxPolarAngle={Math.PI * 0.88}
          target={new THREE.Vector3(...target)}
        />

        <CameraController camPos={camPos} target={target} controlsRef={controlsRef} />

        <SceneRoot pkg={pkg} />
      </Canvas>

      {/* DOM overlay */}
      <div
        style={{
          position: 'absolute',
          top: 12,
          right: 12,
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          pointerEvents: 'none',
        }}
      >
        <button
          onClick={triggerReset}
          style={{
            pointerEvents: 'all',
            background: 'rgba(15,17,23,0.82)',
            border: '1px solid #334155',
            borderRadius: 6,
            color: '#94a3b8',
            fontSize: 12,
            padding: '5px 12px',
            cursor: 'pointer',
            backdropFilter: 'blur(4px)',
          }}
        >
          Reset camera
        </button>
      </div>

      {/* Model info badge */}
      <div
        style={{
          position: 'absolute',
          bottom: 12,
          left: 12,
          fontSize: 11,
          color: '#475569',
          pointerEvents: 'none',
        }}
      >
        {pkg.n_layers} layers · {pkg.n_tokens} tokens · {pkg.n_heads} heads
      </div>
    </div>
  )
}
