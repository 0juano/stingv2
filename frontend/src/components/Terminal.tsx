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
}

export default function Terminal() {
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
  const [currentFlow, setCurrentFlow] = useState(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const { processQuery } = useOrchestrator();

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [messages]);

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

    try {
      // Start the flow visualization
      const result = await processQuery(input, (flow) => {
        setCurrentFlow(flow);
      });

      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'response',
        content: result.response,
        timestamp: new Date(),
        flow: result.flow,
        cost: result.totalCost,
      };

      setMessages(prev => [...prev, responseMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
      setCurrentFlow(null);
    }
  };

  return (
    <div className="min-h-screen bg-background dark p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="terminal rounded-none">
          <div className="terminal-header flex items-center justify-between">
            <span className="text-primary">🏛️ BUREAUCRACY ORACLE</span>
            <span className="text-muted-foreground text-sm">
              BCRA • COMEX • SENASA
            </span>
          </div>
        </div>

        {/* Flow Diagram */}
        <AnimatePresence>
          {currentFlow && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <FlowDiagram flow={currentFlow} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Terminal */}
        <div className="terminal rounded-none">
          <div className="terminal-body" ref={terminalRef}>
            {messages.map((message) => (
              <div key={message.id} className="mb-4">
                {message.type === 'user' && (
                  <div className="flex items-start space-x-2">
                    <span className="text-primary">&gt;</span>
                    <span>{message.content}</span>
                  </div>
                )}
                {message.type === 'system' && (
                  <div className="text-muted-foreground">
                    {message.content}
                  </div>
                )}
                {message.type === 'response' && (
                  <div className="space-y-2">
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    {message.cost !== undefined && (
                      <div className="text-sm text-muted-foreground">
                        💰 Cost: ${message.cost.toFixed(4)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            
            {/* Input Line */}
            <form onSubmit={handleSubmit} className="flex items-start space-x-2">
              <span className="text-primary">&gt;</span>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isProcessing}
                className="flex-1 bg-transparent outline-none font-mono"
                placeholder={isProcessing ? "Processing..." : "Type your question..."}
                autoFocus
              />
              {!isProcessing && <span className="cursor"></span>}
            </form>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setInput("¿Cómo exportar miel a Estados Unidos?")}
            className="agent-box text-sm hover:border-primary transition-colors"
          >
            Export Example
          </button>
          <button
            onClick={() => setInput("¿Cuál es el límite para pagos al exterior?")}
            className="agent-box text-sm hover:border-primary transition-colors"
          >
            BCRA Example
          </button>
          <button
            onClick={() => setInput("¿Qué certificados necesito para importar vacunas?")}
            className="agent-box text-sm hover:border-primary transition-colors"
          >
            Import Example
          </button>
        </div>
      </div>
    </div>
  );
}