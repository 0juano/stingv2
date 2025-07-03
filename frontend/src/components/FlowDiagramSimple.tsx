import { motion } from 'framer-motion';

interface FlowProps {
  flow: {
    currentStep: string;
    routing?: {
      agent?: string;  // old format
      agents?: string[];  // new format
      primary_agent?: string;  // new format
      confidence: number;
      reason: string;
    };
    processing?: string;
    complete?: boolean;
  };
}

const styles = {
  container: {
    border: '2px solid #444',
    backgroundColor: '#1b1b1b',
    padding: '1rem',
    fontFamily: '"Source Code Pro", monospace',
    width: '100%',
    height: '240px',
    boxSizing: 'border-box' as const,
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'center',
  },
  agentBox: {
    border: '2px solid #444',
    backgroundColor: '#2a2a2a',
    padding: '0.375rem 0.75rem',
    display: 'inline-block',
    minWidth: '110px',
    textAlign: 'center' as const,
    fontSize: '0.875rem',
  },
  agentBoxActive: {
    borderColor: '#ff6b35',
    backgroundColor: '#ff6b35',
    color: '#000',
    boxShadow: '0 0 10px #ff6b35',
  },
  connector: {
    color: '#666',
    textAlign: 'center' as const,
    margin: '0.25rem 0',
    fontSize: '0.75rem',
    lineHeight: 1,
  },
};

export default function FlowDiagramSimple({ flow }: FlowProps) {
  const isIdle = flow.currentStep === 'idle';
  
  const getAgentStatus = (agent: string) => {
    // When processing specific agents or in multi-agent mode
    if (flow.currentStep === agent || (flow.currentStep === 'agents' && flow.routing?.agents?.includes(agent))) {
      return 'active';
    }
    
    if (flow.complete && agent === 'auditor') return 'complete';
    
    // Handle multi-agent format
    if (flow.routing) {
      const activeAgents = flow.routing.agents || [];
      if (activeAgents.includes(agent)) return 'selected';
      
      // Handle old single-agent format
      if (flow.routing.agent === agent) return 'selected';
    }
    
    return 'idle';
  };

  const getAgentEmoji = (agent: string) => {
    switch (agent) {
      case 'router': return '🔀';
      case 'bcra': return '🏦';
      case 'comex': return '📦';
      case 'senasa': return '🌾';
      case 'auditor': return '✅';
      default: return '❓';
    }
  };

  return (
    <div style={styles.container}>
      <div style={{ textAlign: 'center', color: '#999', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
        ═══════════ PROCESSING FLOW ═══════════
      </div>

      {/* User Input */}
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <div style={styles.agentBox}>
          👤 USER
        </div>
      </div>

      {/* Arrow down */}
      <div style={{ ...styles.connector, opacity: isIdle ? 0.5 : 1 }}>
        │<br />▼
      </div>

      {/* Router */}
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <motion.div
          style={{
            ...styles.agentBox,
            ...(getAgentStatus('router') === 'active' ? styles.agentBoxActive : {}),
            ...(isIdle ? { opacity: 0.5 } : {}),
          }}
          animate={getAgentStatus('router') === 'active' ? { scale: [1, 1.1, 1] } : {}}
          transition={{ repeat: Infinity, duration: 1 }}
        >
          {getAgentEmoji('router')} ROUTER
          {flow.routing && (
            <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
              {flow.routing.agents && flow.routing.agents.length > 1 ? (
                <>→ {flow.routing.agents.length} agents ({Math.round(flow.routing.confidence * 100)}%)</>
              ) : (
                <>→ {(flow.routing.primary_agent || flow.routing.agent || '').toUpperCase()} ({Math.round(flow.routing.confidence * 100)}%)</>
              )}
            </div>
          )}
        </motion.div>
      </div>

      {/* Branching - Always show the agents */}
      {true && (
        <>
          <div style={{ ...styles.connector, opacity: isIdle ? 0.5 : 1 }}>
            │<br />
            ├────────┬────────┤<br />
            │        │        │
          </div>

          {/* Agents */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginBottom: '1rem' }}>
            {['bcra', 'comex', 'senasa'].map((agent) => (
              <motion.div
                key={agent}
                style={{
                  ...styles.agentBox,
                  ...(getAgentStatus(agent) === 'active' ? styles.agentBoxActive : {}),
                  ...(getAgentStatus(agent) === 'selected' ? { borderColor: '#ff6b35' } : {}),
                  ...(getAgentStatus(agent) === 'idle' && !isIdle ? { opacity: 0.3 } : {}),
                  ...(isIdle ? { opacity: 0.5 } : {}),
                }}
                animate={getAgentStatus(agent) === 'active' ? { scale: [1, 1.1, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                {getAgentEmoji(agent)} {agent.toUpperCase()}
              </motion.div>
            ))}
          </div>

          {/* Converge */}
          <div style={{ ...styles.connector, opacity: isIdle ? 0.5 : 1 }}>
            │        │        │<br />
            └────────┴────────┘<br />
            │<br />▼
          </div>

          {/* Auditor */}
          <div style={{ textAlign: 'center' }}>
            <motion.div
              style={{
                ...styles.agentBox,
                ...(getAgentStatus('auditor') === 'active' ? styles.agentBoxActive : {}),
                ...(isIdle ? { opacity: 0.5 } : {}),
              }}
              animate={getAgentStatus('auditor') === 'active' ? { scale: [1, 1.1, 1] } : {}}
              transition={{ repeat: Infinity, duration: 1 }}
            >
              {getAgentEmoji('auditor')} AUDITOR
            </motion.div>
          </div>
        </>
      )}

      {/* Status Message */}
      {flow.processing && (
        <motion.div
          style={{ textAlign: 'center', color: '#ff6b35', marginTop: '1rem' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          ⚡ {flow.processing}
        </motion.div>
      )}
    </div>
  );
}