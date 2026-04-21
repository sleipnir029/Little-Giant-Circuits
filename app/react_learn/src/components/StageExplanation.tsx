import type { Stage } from '../types'

// Convert **bold** markers to <strong> elements for explanation text.
function renderText(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return parts.map((part, i) =>
    part.startsWith('**') && part.endsWith('**') ? (
      <strong key={i}>{part.slice(2, -2)}</strong>
    ) : (
      <span key={i}>{part}</span>
    )
  )
}

export function StageExplanation({ stage }: { stage: Stage }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* main explanation */}
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#4f6ef7', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
          What's happening
        </div>
        <p style={{ fontSize: 14, color: '#2d3748', lineHeight: 1.65, margin: 0 }}>
          {renderText(stage.explanation)}
        </p>
      </div>

      {/* what changed */}
      <div style={{ borderLeft: '3px solid #e2e8f0', paddingLeft: 12 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
          What changed
        </div>
        <p style={{ fontSize: 13, color: '#718096', lineHeight: 1.55, margin: 0 }}>
          {stage.what_changed}
        </p>
      </div>

      {/* what to notice — highlighted callout */}
      <div
        style={{
          background: '#fffbeb',
          border: '1px solid #f59e0b',
          borderRadius: 8,
          padding: '10px 14px',
        }}
      >
        <div style={{ fontSize: 11, fontWeight: 700, color: '#d97706', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
          ★ What to notice
        </div>
        <p style={{ fontSize: 13, color: '#92400e', lineHeight: 1.55, margin: 0 }}>
          {renderText(stage.what_to_notice)}
        </p>
      </div>

      {/* link to Investigate Mode */}
      {stage.next_technical_view && (
        <div style={{ fontSize: 12, color: '#718096', borderTop: '1px solid #e2e8f0', paddingTop: 10 }}>
          <span style={{ fontWeight: 600 }}>Deeper inspection:</span>{' '}
          Open <em>Investigate Mode → {stage.next_technical_view}</em> in the Streamlit app for
          the full technical view of this computation.
        </div>
      )}
    </div>
  )
}
