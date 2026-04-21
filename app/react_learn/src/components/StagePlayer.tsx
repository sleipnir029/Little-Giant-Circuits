import { useState, useEffect, useRef } from 'react'
import type { LearnPackage } from '../types'
import { PlaybackControls } from './PlaybackControls'
import { StageExplanation } from './StageExplanation'
import { StageViz } from './StageViz'
import { ProgressTimeline } from './ProgressTimeline'

interface StagePlayerProps {
  pkg: LearnPackage
}

export function StagePlayer({ pkg }: StagePlayerProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1500) // ms per stage

  // ref so interval callback always reads latest index (no stale closure)
  const indexRef = useRef(currentIndex)
  indexRef.current = currentIndex

  // Reset to stage 0 when package changes
  useEffect(() => {
    setCurrentIndex(0)
    setIsPlaying(false)
  }, [pkg.task, pkg.trace_id])

  // Auto-advance interval
  useEffect(() => {
    if (!isPlaying) return
    const id = setInterval(() => {
      const next = indexRef.current + 1
      if (next >= pkg.stages.length) {
        setIsPlaying(false)
      } else {
        setCurrentIndex(next)
      }
    }, speed)
    return () => clearInterval(id)
  }, [isPlaying, speed, pkg.stages.length])

  const stage = pkg.stages[currentIndex]
  const total = pkg.stages.length

  function handlePrev() {
    setCurrentIndex((i) => Math.max(0, i - 1))
  }
  function handleNext() {
    setCurrentIndex((i) => Math.min(total - 1, i + 1))
  }
  function handleReset() {
    setCurrentIndex(0)
    setIsPlaying(false)
  }
  function handlePlayPause() {
    // Don't start play from last stage — reset first
    if (!isPlaying && currentIndex === total - 1) {
      setCurrentIndex(0)
    }
    setIsPlaying((p) => !p)
  }

  return (
    <div>
      {/* Stage name + progress */}
      <div
        style={{
          background: '#fff',
          borderRadius: 10,
          border: '1px solid #dde3f0',
          padding: '14px 20px',
          marginBottom: 16,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
          <div>
            <span style={{ fontSize: 12, color: '#9BA8C0' }}>
              {pkg.task} · {pkg.n_tokens} tokens · {pkg.n_layers}-layer model
            </span>
            <h2 style={{ margin: '4px 0 0', fontSize: 17, color: '#1e2a3a', fontWeight: 700 }}>
              {stage.name}
            </h2>
          </div>
          <ProgressTimeline stages={pkg.stages} current={currentIndex} onSelect={setCurrentIndex} />
        </div>

        <div style={{ marginTop: 10 }}>
          <PlaybackControls
            current={currentIndex}
            total={total}
            isPlaying={isPlaying}
            speed={speed}
            onPrev={handlePrev}
            onNext={handleNext}
            onReset={handleReset}
            onPlayPause={handlePlayPause}
            onSpeedChange={setSpeed}
          />
        </div>
      </div>

      {/* Main content: explanation (left) + viz (right) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(260px, 2fr) minmax(280px, 3fr)',
          gap: 16,
          alignItems: 'start',
        }}
      >
        {/* Explanation panel */}
        <div
          style={{
            background: '#fff',
            borderRadius: 10,
            border: '1px solid #dde3f0',
            padding: '20px',
          }}
        >
          <StageExplanation stage={stage} />
        </div>

        {/* Visualization panel */}
        <div
          style={{
            background: '#fff',
            borderRadius: 10,
            border: '1px solid #dde3f0',
            padding: '20px',
            overflowX: 'auto',
          }}
        >
          <div style={{ fontSize: 11, fontWeight: 700, color: '#4a5568', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12 }}>
            Visualization
          </div>
          <StageViz viz={stage.viz} />
        </div>
      </div>
    </div>
  )
}
