import type { LearnPackage } from '../../types'
import { layerY, unembedY } from '../logic/sceneConfig'
import { EmbedPlate } from './EmbedPlate'
import { LayerModule } from './LayerModule'
import { UnembedPlate } from './UnembedPlate'
import { ResidualBus } from './ResidualBus'

interface SceneRootProps {
  pkg: LearnPackage
}

export function SceneRoot({ pkg }: SceneRootProps) {
  const { n_layers, n_tokens } = pkg
  const topY = unembedY(n_layers)

  return (
    <group>
      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[4, 8, 4]} intensity={1.0} />

      {/* Residual bus — runs full height behind everything */}
      <ResidualBus nTokens={n_tokens} nLayers={n_layers} />

      {/* Embed plate at y=0 */}
      <EmbedPlate nTokens={n_tokens} />

      {/* Transformer layers stacked along Y */}
      {Array.from({ length: n_layers }, (_, i) => (
        <LayerModule
          key={i}
          layerIndex={i}
          nTokens={n_tokens}
          y={layerY(i)}
        />
      ))}

      {/* Unembed plate at top */}
      <UnembedPlate nTokens={n_tokens} y={topY} />
    </group>
  )
}
