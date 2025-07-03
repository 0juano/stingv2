import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import FlowDiagramSimple from './FlowDiagramSimple';
import { useOrchestrator } from '../hooks/useOrchestrator';

interface Message {
  id: string;
  type: 'user' | 'system' | 'response';
  content: string;
  timestamp: Date;
  flow?: any;
  cost?: number;
}

const styles = {
  container: {
    height: '100vh',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    fontFamily: '"Source Code Pro", monospace',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    boxSizing: 'border-box' as const,
  },
  terminal: {
    border: '2px solid #444',
    backgroundColor: '#2a2a2a',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.5)',
    width: '600px',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column' as const,
    flex: 1,
  },
  header: {
    backgroundColor: '#333',
    borderBottom: '2px solid #444',
    padding: '0.75rem 1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  body: {
    padding: '1rem',
    overflowY: 'auto' as const,
    flex: '1 1 auto',
    minHeight: 0,  // Important for flex to work properly
  },
  input: {
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#e0e0e0',
    flex: 1,
    fontFamily: 'inherit',
    fontSize: 'inherit',
    resize: 'none' as const,
    minHeight: '1.5em',
    maxHeight: '120px',
    overflow: 'auto' as const,
    wordWrap: 'break-word' as const,
    whiteSpace: 'pre-wrap' as const,
  },
  cursor: {
    display: 'inline-block',
    width: '10px',
    height: '20px',
    backgroundColor: '#ff6b35',
    animation: 'blink 1s infinite',
  },
  button: {
    border: '2px solid #444',
    backgroundColor: '#2a2a2a',
    color: '#e0e0e0',
    padding: '0.5rem 1rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontSize: '0.875rem',
  },
};

export default function TerminalSimple() {
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
  const [currentFlow, setCurrentFlow] = useState<any>({ currentStep: 'idle' });
  const [showFlow, setShowFlow] = useState(false);  // Start with flow hidden
  const terminalRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { processQuery } = useOrchestrator();

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  useEffect(() => {
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
      setShowFlow(true);
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
      // Hide flow diagram after response
      setTimeout(() => setShowFlow(false), 1000);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
      setCurrentFlow({ currentStep: 'idle' });
    }
  };

  return (
    <div style={styles.container}>
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600&display=swap');
          
          @keyframes blink {
            0%, 49% { opacity: 1; }
            50%, 100% { opacity: 0; }
          }
          
          .terminal-body::-webkit-scrollbar {
            width: 12px;
          }
          
          .terminal-body::-webkit-scrollbar-track {
            background: #333;
          }
          
          .terminal-body::-webkit-scrollbar-thumb {
            background: #555;
            border: 2px solid #333;
          }
        `}
      </style>
      
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', width: '100%' }}>
        {/* Main Terminal */}
        <div style={{ ...styles.terminal, flex: '1 1 auto', minHeight: 0, display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <div style={styles.header}>
            <span style={{ color: '#ff6b35' }}>🏛️ BUREAUCRACY ORACLE</span>
            <span style={{ color: '#999', fontSize: '0.875rem' }}>
              BCRA • COMEX • SENASA
            </span>
          </div>

          {/* Flow Diagram Container - Fixed height */}
          <div style={{ 
            height: showFlow ? '280px' : '0px',
            overflow: 'hidden',
            transition: 'height 0.3s ease-in-out',
            borderBottom: showFlow ? '2px solid #444' : 'none'
          }}>
            <div style={{ padding: '1rem' }}>
              <FlowDiagramSimple flow={currentFlow} />
            </div>
          </div>
          <div style={styles.body} ref={terminalRef} className="terminal-body">
            {messages.map((message) => (
              <div key={message.id} style={{ marginBottom: '1rem' }}>
                {message.type === 'user' && (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{ color: '#ff6b35' }}>&gt;</span>
                    <span>{message.content}</span>
                  </div>
                )}
                {message.type === 'system' && (
                  <div style={{ color: '#999' }}>
                    {message.content}
                  </div>
                )}
                {message.type === 'response' && (
                  <div>
                    <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                    {message.cost !== undefined && (
                      <div style={{ color: '#999', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        💰 Cost: ${message.cost.toFixed(4)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            
            {/* Input Line */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
              <span style={{ color: '#ff6b35', marginTop: '0.25rem' }}>&gt;</span>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  adjustTextareaHeight();
                  // Show flow diagram when user starts typing
                  if (e.target.value && !showFlow) {
                    setShowFlow(true);
                    setCurrentFlow({ currentStep: 'idle' });
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                disabled={isProcessing}
                style={styles.input}
                placeholder={isProcessing ? "Processing..." : "Type your question..."}
                rows={1}
                autoFocus
              />
              {!isProcessing && <span style={styles.cursor}></span>}
            </form>
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', marginBottom: '1rem', flexWrap: 'wrap', width: '600px', flex: 'none' }}>
          <button
            onClick={() => setInput("¿Cómo exportar miel a Estados Unidos?")}
            style={styles.button}
          >
            Export Example
          </button>
          <button
            onClick={() => setInput("¿Cuál es el límite para pagos al exterior?")}
            style={styles.button}
          >
            BCRA Example
          </button>
          <button
            onClick={() => setInput("¿Qué certificados necesito para importar vacunas?")}
            style={styles.button}
          >
            Import Example
          </button>
        </div>
      </div>
    </div>
  );
}