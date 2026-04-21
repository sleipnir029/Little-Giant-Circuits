interface PlaybackControlsProps {
  current: number
  total: number
  isPlaying: boolean
  speed: number // ms per stage
  onPrev: () => void
  onNext: () => void
  onReset: () => void
  onPlayPause: () => void
  onSpeedChange: (ms: number) => void
}

const SPEED_OPTIONS = [
  { label: '0.5×', ms: 3000 },
  { label: '1×', ms: 1500 },
  { label: '2×', ms: 750 },
  { label: '4×', ms: 375 },
]

export function PlaybackControls({
  current,
  total,
  isPlaying,
  speed,
  onPrev,
  onNext,
  onReset,
  onPlayPause,
  onSpeedChange,
}: PlaybackControlsProps) {
  const btnBase: React.CSSProperties = {
    padding: '6px 14px',
    borderRadius: 6,
    border: '1px solid #dde3f0',
    background: '#fff',
    color: '#4a5568',
    fontSize: 13,
    cursor: 'pointer',
    fontWeight: 500,
    transition: 'all 0.1s',
  }
  const btnActive: React.CSSProperties = {
    ...btnBase,
    background: '#4f6ef7',
    color: '#fff',
    border: '1px solid #4f6ef7',
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        flexWrap: 'wrap',
        padding: '10px 0',
      }}
    >
      {/* Reset */}
      <button onClick={onReset} style={btnBase} title="Reset to first stage">
        ↩
      </button>

      {/* Prev */}
      <button onClick={onPrev} disabled={current === 0} style={{ ...btnBase, opacity: current === 0 ? 0.4 : 1 }}>
        ← Prev
      </button>

      {/* Play / Pause */}
      <button onClick={onPlayPause} style={btnActive}>
        {isPlaying ? '⏸ Pause' : '▶ Play'}
      </button>

      {/* Next */}
      <button onClick={onNext} disabled={current === total - 1} style={{ ...btnBase, opacity: current === total - 1 ? 0.4 : 1 }}>
        Next →
      </button>

      {/* step counter */}
      <span style={{ fontSize: 12, color: '#718096', marginLeft: 4 }}>
        {current + 1} / {total}
      </span>

      {/* Speed buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginLeft: 8 }}>
        <span style={{ fontSize: 11, color: '#9BA8C0' }}>Speed:</span>
        {SPEED_OPTIONS.map((opt) => (
          <button
            key={opt.ms}
            onClick={() => onSpeedChange(opt.ms)}
            style={speed === opt.ms ? { ...btnActive, padding: '4px 8px', fontSize: 11 } : { ...btnBase, padding: '4px 8px', fontSize: 11 }}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
