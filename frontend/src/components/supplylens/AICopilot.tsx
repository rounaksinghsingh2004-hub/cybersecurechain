import { useState } from 'react'
import { AlertTriangle, Bot, Brain, CheckCircle2, ChevronRight, HelpCircle, Lightbulb, RefreshCw, Send, ShieldAlert, Sparkles } from 'lucide-react'
import { Metric, Panel, Status } from '../common'
import { post } from '../../services/api'

const PRESET_QUERIES = [
  'Explain the operational risk of Log4Shell on fulfillment centers',
  'Which suppliers present the highest risk to order operations?',
  'Summarize all CISA KEV vulnerabilities across our codebases',
  'Recommend prioritized remediation actions for critical CVEs',
  'How does PyYAML vulnerability affect the inventory service?',
]

export function AICopilot() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<any>(null)
  const [error, setError] = useState('')

  const handleQuery = async (queryText?: string) => {
    const q = queryText || prompt
    if (!q.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await post<any>('/api/supplylens/copilot/query', { prompt: q })
      setResponse(res)
    } catch (err: any) {
      setError(err.message || 'Failed to get copilot analysis')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <span className="eyebrow">SUPPLYLENS AI · INTELLIGENT DECISION SUPPORT</span>
          <h2>AI Risk Copilot</h2>
          <p>
            Evidence-grounded risk reasoning for software supply chains. Every insight is derived directly
            from stored SBOM inventory, CVE findings, and cyber-physical mappings with transparent deterministic fallback.
          </p>
        </div>
        <span className="safety">EVIDENCE GROUNDED ONLY</span>
      </section>

      <section className="metric-grid">
        <Metric label="Copilot Engine" value="Hybrid Rule+LLM" note="Deterministic fallback ready" />
        <Metric label="Grounding Base" value="Local SQLite Twin" tone="teal" note="Zero external hallucination" />
        <Metric label="Response Mode" value="Deterministic Grounded" tone="gold" note="Explainable scoring" />
        <Metric label="Safety Guard" value="Enforced" tone="teal" note="No DB mutation capability" />
      </section>

      <Panel title="Ask SupplyLens Copilot">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              type="text"
              placeholder="Ask about software vulnerabilities, supplier exposure, or facility risk..."
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleQuery()}
              style={{
                flex: 1,
                background: '#0a1620',
                border: '1px solid #1e3344',
                color: '#c0d8e0',
                borderRadius: 6,
                padding: '12px 16px',
                fontSize: 13,
                outline: 'none',
              }}
            />
            <button
              className="launch-button"
              disabled={loading || !prompt.trim()}
              onClick={() => handleQuery()}
              style={{ padding: '0 20px', display: 'flex', alignItems: 'center', gap: 8 }}
            >
              <Send size={15} />
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>

          <div>
            <span style={{ fontSize: 11, color: '#8ca7af', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
              <Lightbulb size={13} color="#e8bd68" /> Suggested Questions:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {PRESET_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setPrompt(q)
                    handleQuery(q)
                  }}
                  className="quiet-button"
                  style={{ fontSize: 11, padding: '5px 10px', background: 'rgba(92, 224, 192, 0.05)', borderColor: '#2d4a52', color: '#8da1ad' }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Panel>

      {error && (
        <div className="error-box">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {response && (
        <Panel title="Copilot Analysis Report" action={<Status value={response.confidence_level || 'HIGH'} />}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Executive Summary */}
            <div style={{ background: '#0a1620', border: '1px solid #1a3040', borderRadius: 6, padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#5CE0C0', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>
                <Brain size={16} /> EXECUTIVE SUMMARY
              </div>
              <p style={{ color: '#e2eef2', fontSize: 13, lineHeight: 1.6, margin: 0 }}>
                {response.summary || response.analysis || JSON.stringify(response)}
              </p>
            </div>

            {/* Key Risks */}
            {response.key_risks?.length > 0 && (
              <div style={{ background: '#0a1620', border: '1px solid #1a3040', borderRadius: 6, padding: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#eb6969', fontWeight: 700, fontSize: 13, marginBottom: 8 }}>
                  <ShieldAlert size={16} /> KEY EXPOSURE RISKS
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {response.key_risks.map((risk: string, i: number) => (
                    <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', fontSize: 12, color: '#c0d8e0' }}>
                      <span style={{ color: '#eb6969', fontWeight: 'bold' }}>•</span>
                      <span>{risk}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommended Mitigations */}
            {response.recommended_actions?.length > 0 && (
              <div style={{ background: '#0a1620', border: '1px solid #1a3040', borderRadius: 6, padding: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#42b7c2', fontWeight: 700, fontSize: 13, marginBottom: 8 }}>
                  <CheckCircle2 size={16} /> RECOMMENDED MITIGATIONS
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {response.recommended_actions.map((act: string, i: number) => (
                    <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', fontSize: 12, color: '#c0d8e0' }}>
                      <span style={{ color: '#42b7c2', fontWeight: 'bold' }}>✓</span>
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Grounded Evidence Details */}
            {response.evidence && (
              <div style={{ fontSize: 11, color: '#6a8fa0', borderTop: '1px solid #1a2e3a', paddingTop: 10 }}>
                <strong>Evidence Grounding:</strong> Model reasoning based on {response.evidence.findings_count || 0} CVE findings and {response.evidence.deployments_count || 0} verified physical deployment mappings.
              </div>
            )}
          </div>
        </Panel>
      )}
    </div>
  )
}
