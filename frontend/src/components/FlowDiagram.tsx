import React from 'react';
import { motion } from 'framer-motion';

interface FlowProps {
  flow: {
    currentStep: string;
    routing?: {
      agent: string;
      confidence: number;
      reason: string;
    };
    processing?: string;
    complete?: boolean;
  };
}

export default function FlowDiagram({ flow }: FlowProps) {
  const agents = ['router', 'bcra', 'comex', 'senasa', 'auditor'];
  
  const getAgentStatus = (agent: string) => {
    if (flow.currentStep === agent) return 'active';
    if (flow.complete && agent === 'auditor') return 'complete';
    if (flow.routing && flow.routing.agent === agent) return 'selected';
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
    <div className="terminal rounded-none p-6 font-mono text-sm">
      <div className="space-y-4">
        {/* Header */}
        <div className="text-center text-muted-foreground">
          ═══════════ PROCESSING FLOW ═══════════
        </div>

        {/* User Input */}
        <div className="flex justify-center">
          <div className="agent-box">
            👤 USER
          </div>
        </div>

        {/* Arrow down */}
        <div className="text-center text-muted-foreground">
          │<br />▼
        </div>

        {/* Router */}
        <div className="flex justify-center">
          <motion.div
            className={`agent-box ${getAgentStatus('router') === 'active' ? 'active' : ''}`}
            animate={getAgentStatus('router') === 'active' ? { scale: [1, 1.1, 1] } : {}}
            transition={{ repeat: Infinity, duration: 1 }}
          >
            {getAgentEmoji('router')} ROUTER
            {flow.routing && (
              <div className="text-xs mt-1">
                → {flow.routing.agent.toUpperCase()} ({Math.round(flow.routing.confidence * 100)}%)
              </div>
            )}
          </motion.div>
        </div>

        {/* Branching */}
        {flow.routing && (
          <>
            <div className="text-center text-muted-foreground">
              │<br />
              ├────────┬────────┤<br />
              │        │        │
            </div>

            {/* Agents */}
            <div className="flex justify-center space-x-8">
              {['bcra', 'comex', 'senasa'].map((agent) => (
                <motion.div
                  key={agent}
                  className={`agent-box ${
                    getAgentStatus(agent) === 'active' ? 'active' :
                    getAgentStatus(agent) === 'selected' ? 'border-primary' : 
                    'opacity-50'
                  }`}
                  animate={getAgentStatus(agent) === 'active' ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ repeat: Infinity, duration: 1 }}
                >
                  {getAgentEmoji(agent)} {agent.toUpperCase()}
                </motion.div>
              ))}
            </div>

            {/* Converge */}
            <div className="text-center text-muted-foreground">
              │        │        │<br />
              └────────┴────────┘<br />
              │<br />▼
            </div>

            {/* Auditor */}
            <div className="flex justify-center">
              <motion.div
                className={`agent-box ${getAgentStatus('auditor') === 'active' ? 'active' : ''}`}
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
            className="text-center text-primary mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            ⚡ {flow.processing}
          </motion.div>
        )}
      </div>
    </div>
  );
}