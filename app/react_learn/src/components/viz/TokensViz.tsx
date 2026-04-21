import type { TokensData } from '../../types'

export function TokensViz({ data }: { data: TokensData }) {
  return (
    <div>
      <p style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
        Each box is one token. The number is the token's integer ID in the model vocabulary.
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'flex-end' }}>
        {data.token_labels.map((label, i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <div
              style={{
                padding: '10px 16px',
                background: '#eef1fe',
                border: '2px solid #4f6ef7',
                borderRadius: 8,
                fontSize: 18,
                fontWeight: 700,
                color: '#3730a3',
                fontFamily: 'monospace',
                minWidth: 44,
              }}
            >
              {label}
            </div>
            <div style={{ fontSize: 11, color: '#9BA8C0', marginTop: 4 }}>pos {data.positions[i]}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 16, fontSize: 12, color: '#718096' }}>
        <strong>Vocab size:</strong> {Math.max(...data.tokens) + 1}+ &nbsp;|&nbsp;
        <strong>Sequence length:</strong> {data.tokens.length} tokens
      </div>
    </div>
  )
}
