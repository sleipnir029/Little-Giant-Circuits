import { useState } from 'react'
import { useLearnData } from './hooks/useLearnData'
import { StagePlayer } from './components/StagePlayer'
import { SpatialViewer } from './spatial/SpatialViewer'
import type { ManifestEntry } from './types'

type ViewMode = 'spatial' | 'flat'

const TASK_DESCRIPTIONS: Record<string, string> = {
  induction: 'Pattern completion — given [A B … A], predict B',
  kv_retrieval: 'In-context lookup — given key-value pairs, retrieve the value for a query key',
  modular_arith: 'Modular addition — compute (a + b) mod p',
  bracket_match: 'Bracket balancing — track open/close depth across a sequence',
  sorting: 'Reversal/sorting — reorder a sequence of tokens',
  factual_lookup: 'Subject→attribute recall — predict an attribute given a subject token',
}

export default function App() {
  const { manifest, selectedPackage, loadingManifest, loadingPackage, manifestError, packageError, selectTask } =
    useLearnData()

  const [selectedEntry, setSelectedEntry] = useState<ManifestEntry | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('spatial')

  function handleSelect(entry: ManifestEntry) {
    setSelectedEntry(entry)
    selectTask(entry.task, entry.trace_id)
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f7f8fc', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Header */}
      <header
        style={{
          background: '#fff',
          borderBottom: '1px solid #dde3f0',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          height: 56,
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <span style={{ fontSize: 18, fontWeight: 800, color: '#1e2a3a', letterSpacing: '-0.02em' }}>
            Little Giant Circuits
          </span>
          <span
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: '#4f6ef7',
              background: '#eef1fe',
              padding: '2px 8px',
              borderRadius: 4,
            }}
          >
            Learn Mode
          </span>
        </div>

        {/* View mode tab toggle */}
        <div
          style={{
            display: 'flex',
            gap: 2,
            background: '#f0f4ff',
            borderRadius: 7,
            padding: 2,
            border: '1px solid #dde3f0',
          }}
        >
          {(['spatial', 'flat'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              style={{
                padding: '4px 14px',
                fontSize: 12,
                fontWeight: 600,
                borderRadius: 5,
                border: 'none',
                cursor: 'pointer',
                background: viewMode === mode ? '#fff' : 'transparent',
                color: viewMode === mode ? '#1e2a3a' : '#9BA8C0',
                boxShadow: viewMode === mode ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.12s',
                textTransform: 'capitalize',
              }}
            >
              {mode === 'spatial' ? 'Spatial' : 'Flat'}
            </button>
          ))}
        </div>

        <div style={{ flex: 1 }} />

        {/* Task selector */}
        {manifest && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 12, color: '#718096' }}>Task:</span>
            <select
              value={selectedEntry?.task ?? selectedPackage?.task ?? ''}
              onChange={(e) => {
                const entry = manifest.packages.find((p) => p.task === e.target.value)
                if (entry) handleSelect(entry)
              }}
              style={{
                border: '1px solid #dde3f0',
                borderRadius: 6,
                padding: '5px 10px',
                fontSize: 13,
                color: '#2d3748',
                background: '#fff',
                cursor: 'pointer',
              }}
            >
              {manifest.packages.map((p) => (
                <option key={p.task} value={p.task}>
                  {p.task} ({p.n_tokens} tokens, {p.n_stages} stages)
                </option>
              ))}
            </select>
          </div>
        )}

        <a
          href="http://localhost:8501"
          target="_blank"
          rel="noopener noreferrer"
          style={{ fontSize: 12, color: '#4f6ef7', textDecoration: 'none', flexShrink: 0 }}
        >
          Investigate Mode →
        </a>
      </header>

      {/* Main content — Spatial view fills full viewport height, Flat view is scrollable */}
      <main
        style={
          viewMode === 'spatial'
            ? { height: 'calc(100vh - 56px)', display: 'flex', flexDirection: 'column' }
            : { maxWidth: 1100, margin: '0 auto', padding: '24px 16px' }
        }
      >
        {/* Error: manifest failed to load */}
        {manifestError && (
          <div
            style={{
              background: '#fff5f5',
              border: '1px solid #feb2b2',
              borderRadius: 10,
              padding: 24,
              marginBottom: 24,
            }}
          >
            <h3 style={{ margin: '0 0 8px', color: '#c53030', fontSize: 16 }}>Learn data not found</h3>
            <p style={{ margin: '0 0 12px', color: '#742a2a', fontSize: 14 }}>
              Could not load <code>/learn_data/manifest.json</code>. The learn data packages must be
              generated before this app can run.
            </p>
            <pre
              style={{
                background: '#1e2a3a',
                color: '#9ae6b4',
                padding: 12,
                borderRadius: 6,
                fontSize: 13,
                overflowX: 'auto',
              }}
            >
              {`# From the project root:
source .venv/bin/activate
python scripts/export_learn_stages.py`}
            </pre>
            <p style={{ margin: '8px 0 0', color: '#718096', fontSize: 12 }}>
              This generates <code>learn_data/</code> from existing trace files.
              Traces are generated with <code>python scripts/generate_demo_traces.py</code> if missing.
            </p>
          </div>
        )}

        {/* Loading */}
        {loadingManifest && (
          <div style={{ textAlign: 'center', padding: 60, color: '#9BA8C0' }}>
            Loading…
          </div>
        )}

        {/* Package loading */}
        {loadingPackage && (
          <div style={{ textAlign: 'center', padding: 60, color: '#9BA8C0' }}>
            Loading trace…
          </div>
        )}

        {/* Package error */}
        {packageError && !loadingPackage && (
          <div
            style={{
              background: '#fff5f5',
              border: '1px solid #feb2b2',
              borderRadius: 8,
              padding: 16,
              color: '#c53030',
              fontSize: 13,
              margin: viewMode === 'spatial' ? '16px' : undefined,
            }}
          >
            Failed to load package: {packageError}
          </div>
        )}

        {/* Spatial view — fills remaining height */}
        {viewMode === 'spatial' && selectedPackage && !loadingPackage && !packageError && (
          <div style={{ flex: 1, minHeight: 0 }}>
            <SpatialViewer pkg={selectedPackage} />
          </div>
        )}

        {/* Flat view — task description + stage player + footer */}
        {viewMode === 'flat' && (
          <>
            {selectedPackage && !loadingPackage && (
              <div
                style={{
                  background: '#eef1fe',
                  borderRadius: 8,
                  padding: '10px 16px',
                  marginBottom: 16,
                  fontSize: 13,
                  color: '#3730a3',
                }}
              >
                <strong>{selectedPackage.task}:</strong>{' '}
                {TASK_DESCRIPTIONS[selectedPackage.task] ?? 'Toy synthetic task'}
                <span style={{ color: '#6366f1', marginLeft: 12 }}>
                  {selectedPackage.n_layers}-layer model · d_model={selectedPackage.d_model} · {selectedPackage.n_heads} heads
                </span>
              </div>
            )}

            {selectedPackage && !loadingPackage && !packageError && (
              <StagePlayer pkg={selectedPackage} />
            )}

            <footer
              style={{
                marginTop: 32,
                paddingTop: 16,
                borderTop: '1px solid #e2e8f0',
                fontSize: 12,
                color: '#9BA8C0',
                textAlign: 'center',
              }}
            >
              Learn Mode shows a single forward pass, stage by stage. For full technical
              inspection (all layers, attention patterns, MLP neurons, logit evolution), use{' '}
              <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer" style={{ color: '#4f6ef7' }}>
                Investigate Mode in Streamlit
              </a>
              .
            </footer>
          </>
        )}
      </main>
    </div>
  )
}
