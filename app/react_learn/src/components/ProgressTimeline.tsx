interface ProgressTimelineProps {
  stages: { name: string }[]
  current: number
  onSelect: (index: number) => void
}

export function ProgressTimeline({ stages, current, onSelect }: ProgressTimelineProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 0,
        overflowX: 'auto',
        padding: '8px 0',
      }}
    >
      {stages.map((stage, i) => {
        const isPast = i < current
        const isCurrent = i === current
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
            <button
              onClick={() => onSelect(i)}
              title={stage.name}
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                border: isCurrent ? '2px solid #4f6ef7' : '2px solid #e2e8f0',
                background: isCurrent ? '#4f6ef7' : isPast ? '#c7d2fe' : '#f7f8fc',
                color: isCurrent ? '#fff' : isPast ? '#4f46e5' : '#9BA8C0',
                fontSize: 11,
                fontWeight: isCurrent ? 700 : 500,
                cursor: 'pointer',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.15s ease',
              }}
            >
              {i + 1}
            </button>
            {i < stages.length - 1 && (
              <div
                style={{
                  width: 20,
                  height: 2,
                  background: i < current ? '#c7d2fe' : '#e2e8f0',
                  flexShrink: 0,
                }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
