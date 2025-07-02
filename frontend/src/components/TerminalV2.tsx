import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import FlowDiagram from './FlowDiagram';
import { useOrchestrator } from '../hooks/useOrchestrator';

interface Message {
  id: string;
  type: 'user' | 'system' | 'response';
  content: string;
  timestamp: Date;
  flow?: any;
  cost?: number;
  agentsConsulted?: string[];
}

export default function TerminalV2() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'BUREAUCRACY ORACLE v1.0 - Argentine Regulations Assistant',
      timestamp: new Date(),
    },
    {
      id: '2',
      type: 'system',
      content: 'Type your question about imports, exports, or financial regulations...',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentFlow, setCurrentFlow] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [showMobileLogs, setShowMobileLogs] = useState(false);
  
  const chatRef = useRef<HTMLDivElement>(null);
  const logsRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { processQuery } = useOrchestrator();

  useEffect(() => {
    // Auto-scroll chat to bottom
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    // Auto-scroll logs to bottom
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight;
    }
  }, [logs]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    
    // Clear previous logs
    setLogs([]);
    addLog('> New query received');
    addLog(`> Processing: "${input.substring(0, 50)}${input.length > 50 ? '...' : ''}"`);

    const startTime = Date.now();

    try {
      const result = await processQuery(input, (flow) => {
        setCurrentFlow(flow);
        
        // Log flow updates with enhanced formatting
        if (flow.currentStep === 'router' && flow.routing) {
          const confidence = Math.round((flow.routing.confidence || 0) * 100);
          addLog(`> Router: intent classified — ${confidence}% confidence`);
          
          if (flow.routing.agents && flow.routing.agents.length > 0) {
            addLog(`> ↳ Agents: ${flow.routing.agents.map((a: string) => a.toUpperCase()).join(', ')}`);
          }
        }
        
        if (flow.currentStep === 'agents' && flow.stepData?.agentCount > 1) {
          addLog(`> Calling ${flow.stepData.agentCount} agents in parallel...`);
        }
        
        if (flow.routing?.agents?.includes(flow.currentStep)) {
          addLog(`> ${flow.currentStep.toUpperCase()} ✔︎`);
        }
        
        if (flow.currentStep === 'auditor') {
          const action = flow.stepData?.isMultiAgent ? 'merging responses' : 'validating response';
          addLog(`> Auditor ${action}...`);
        }
        
        if (flow.processing && !flow.processing.includes('Consultando')) {
          addLog(`> ${flow.processing}`);
        }
      });

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      addLog(`> Done in ${elapsed}s`);
      
      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'response',
        content: result.response,
        timestamp: new Date(),
        flow: result.flow,
        cost: result.totalCost,
        agentsConsulted: result.agentsConsulted,
      };

      setMessages(prev => [...prev, responseMessage]);
    } catch (error) {
      addLog(`> Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
      setCurrentFlow(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0a0a]">
      {/* Chat sidebar - fixed width */}
      <aside className="w-[360px] bg-[#1b1b1b] flex flex-col border-r border-gray-800">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-[#ff6b35] font-bold text-lg">🏛️ BUREAUCRACY ORACLE</h1>
          <p className="text-gray-500 text-xs mt-1">BCRA • COMEX • SENASA</p>
        </div>

        {/* Messages container - fixed height */}
        <div 
          ref={chatRef}
          className="flex-1 h-[400px] overflow-y-auto p-4 space-y-4 custom-scrollbar"
        >
          {messages.map((message) => (
            <div key={message.id} className="text-sm">
              {message.type === 'user' && (
                <div className="flex items-start space-x-2">
                  <span className="text-[#ff6b35]">&gt;</span>
                  <span className="text-gray-200 break-words">{message.content}</span>
                </div>
              )}
              {message.type === 'system' && (
                <div className="text-gray-500 italic">{message.content}</div>
              )}
              {message.type === 'response' && (
                <div className="space-y-2 text-gray-300">
                  <div className="whitespace-pre-wrap break-words">{message.content}</div>
                  <div className="text-xs text-gray-500 space-y-1">
                    {message.agentsConsulted && message.agentsConsulted.length > 0 && (
                      <div>🤝 Agents: {message.agentsConsulted.map(a => a.toUpperCase()).join(', ')}</div>
                    )}
                    {message.cost !== undefined && (
                      <div className="font-ibm-mono">💰 Cost: ${message.cost.toFixed(4)}</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input area */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
          <div className="flex items-start space-x-2">
            <span className="text-[#ff6b35] mt-2">&gt;</span>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                adjustTextareaHeight();
              }}
              onKeyDown={handleKeyDown}
              disabled={isProcessing}
              className="flex-1 bg-transparent outline-none font-code text-sm text-gray-200 resize-none overflow-y-auto whitespace-pre-wrap break-words custom-scrollbar"
              placeholder={isProcessing ? "Processing..." : "Type your question..."}
              rows={3}
              maxLength={800}
              autoFocus
            />
          </div>
        </form>
      </aside>

      {/* Main content area - Flow diagram */}
      <section className="flex-1 overflow-y-auto p-6 bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto">
          <FlowDiagram flow={currentFlow || { currentStep: 'idle' }} />
          
          {/* Quick Actions */}
          <div className="mt-6 flex flex-wrap gap-2">
            <button
              onClick={() => setInput("¿Cómo exportar miel a Estados Unidos?")}
              className="px-4 py-2 bg-[#1b1b1b] border border-gray-700 text-gray-300 text-sm hover:border-[#ff6b35] transition-colors"
            >
              Export Example
            </button>
            <button
              onClick={() => setInput("¿Cuál es el límite para pagos al exterior?")}
              className="px-4 py-2 bg-[#1b1b1b] border border-gray-700 text-gray-300 text-sm hover:border-[#ff6b35] transition-colors"
            >
              BCRA Example
            </button>
            <button
              onClick={() => setInput("¿Qué certificados necesito para importar vacunas?")}
              className="px-4 py-2 bg-[#1b1b1b] border border-gray-700 text-gray-300 text-sm hover:border-[#ff6b35] transition-colors"
            >
              Import Example
            </button>
          </div>
        </div>
      </section>

      {/* Terminal log panel - desktop only */}
      <section className="w-80 bg-black text-[#00ff88] font-code p-4 overflow-y-auto hidden lg:block border-l border-gray-800 custom-scrollbar">
        <h2 className="text-sm mb-4 opacity-75 font-ibm-mono">INTERNAL LOGS</h2>
        <pre ref={logsRef} className="text-xs leading-relaxed">
          {logs.length === 0 ? '> Waiting for queries...' : logs.join('\n')}
        </pre>
      </section>

      {/* Mobile logs toggle button */}
      <button
        onClick={() => setShowMobileLogs(!showMobileLogs)}
        className="fixed bottom-4 right-4 lg:hidden bg-black text-[#00ff88] p-3 rounded-full shadow-lg z-10"
      >
        {showMobileLogs ? '✕' : '📜'}
      </button>

      {/* Mobile logs panel */}
      <AnimatePresence>
        {showMobileLogs && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            className="fixed inset-x-0 bottom-0 h-1/2 bg-black text-[#00ff88] font-code p-4 overflow-y-auto lg:hidden z-20 border-t border-gray-800 custom-scrollbar"
          >
            <h2 className="text-sm mb-4 opacity-75 font-ibm-mono">INTERNAL LOGS</h2>
            <pre className="text-xs leading-relaxed">
              {logs.length === 0 ? '> Waiting for queries...' : logs.join('\n')}
            </pre>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}