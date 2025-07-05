import React, { useState, useRef, useEffect } from 'react';
import FlowDiagramSimple from './FlowDiagramSimple';
import { useOrchestrator } from '../hooks/useOrchestrator';
import { getInitialGreeting, getInitialInstruction, getInputPlaceholder, getProcessingPlaceholder } from '../utils/bureaucratMessages';

interface Message {
  id: string;
  type: 'user' | 'system' | 'response';
  content: string;
  timestamp: Date;
  flow?: any;
  cost?: number;
  duration?: number;
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
    width: '100%',
    maxWidth: '600px',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column' as const,
    flex: 1,
    height: '100%',  // Ensure it takes full height of its container
    maxHeight: 'calc(100vh - 8rem)',  // Leave some margin for padding
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
    overflow: 'hidden',  // Hide scrollbar
    wordWrap: 'break-word' as const,
    whiteSpace: 'pre-wrap' as const,
    lineHeight: '1.5',
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
  submitButton: {
    border: '2px solid #ff6b35',
    backgroundColor: '#2a2a2a',
    color: '#ff6b35',
    padding: '0.75rem 1.5rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontSize: '1rem',
    fontWeight: '600',
    minWidth: '80px',
    minHeight: '44px',
  },
};

export default function TerminalSimple() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: getInitialGreeting(),
      timestamp: new Date(),
    },
    {
      id: '2',
      type: 'system',
      content: getInitialInstruction(),
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentFlow, setCurrentFlow] = useState<any>({ currentStep: 'idle' });
  const [showFlow, setShowFlow] = useState(true);  // Start with flow visible
  const [isMobile, setIsMobile] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { processQuery } = useOrchestrator();

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  useEffect(() => {
    if (terminalRef.current && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      // If the last message is a response, scroll to top so user can read from beginning
      if (lastMessage.type === 'response') {
        terminalRef.current.scrollTop = 0;
      } else {
        // For user and system messages, scroll to bottom
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }
    }
  }, [messages]);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    // Handle global keyboard shortcuts
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === '/' && textareaRef.current && document.activeElement !== textareaRef.current) {
        e.preventDefault();
        textareaRef.current.focus();
      } else if (e.key === 'Escape' && document.activeElement !== textareaRef.current) {
        // If we have responses and Escape is pressed (not in input), go back to original screen
        if (messages.some(m => m.type === 'response')) {
          e.preventDefault();
          setMessages([
            {
              id: '1',
              type: 'system',
              content: getInitialGreeting(),
              timestamp: new Date(),
            },
            {
              id: '2',
              type: 'system',
              content: getInitialInstruction(),
              timestamp: new Date(),
            },
          ]);
          setShowFlow(true);
          setCurrentFlow({ currentStep: 'idle' });
          setInput('');
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.group('🎯 [UI] Form Submission');
    console.log('📝 Input:', input);
    console.log('🔄 Processing:', isProcessing);
    console.log('📱 Mobile mode:', isMobile);
    console.groupEnd();
    
    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    console.log('💬 [UI] Adding user message:', userMessage);
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    
    try {
      console.log('🔮 [UI] Showing flow diagram');
      setShowFlow(true);
      const result = await processQuery(input, (flow) => {
        console.log('🔄 [UI] Flow update:', flow.currentStep);
        setCurrentFlow(flow);
        
        // Processing logs removed for simplified UI
      });

      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'response',
        content: result.response,
        timestamp: new Date(),
        flow: result.flow,
        cost: result.totalCost,
        duration: result.duration,
      };

      console.log('✅ [UI] Query successful:', {
        success: result.success,
        duration: result.duration,
        cost: result.totalCost,
        responseLength: result.response.length
      });

      setMessages(prev => [...prev, responseMessage]);
      // Hide flow diagram immediately when response arrives
      setShowFlow(false);
    } catch (error: any) {
      console.error('❌ [UI] Query failed:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      console.log('🏁 [UI] Resetting UI state');
      setIsProcessing(false);
      setCurrentFlow({ currentStep: 'idle' });
      // Keep flow hidden after processing
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
          
          /* Mobile styles */
          @media (max-width: 768px) {
            .container {
              padding: 0 !important;
              width: 100vw !important;
              overflow-x: hidden !important;
            }
            
            .terminal {
              max-height: 100vh !important;
              border: none !important;
              box-shadow: none !important;
              background-color: transparent !important;
              width: 100% !important;
              max-width: 100vw !important;
              margin: 0 !important;
            }
            
            .terminal-header {
              padding: 0.75rem 0.5rem !important;
              font-size: 1rem !important;
              background-color: #1a1a1a !important;
              border-bottom: 1px solid #333 !important;
            }
            
            .terminal-header span {
              font-size: 0.9rem !important;
            }
            
            .terminal-body {
              padding: 1rem 0.75rem !important;
              font-size: 1rem !important;
              line-height: 1.6 !important;
            }
            
            .quick-actions {
              grid-template-columns: 1fr !important;
              gap: 0.5rem !important;
              padding: 0 1rem !important;
              margin: 0.5rem 0 !important;
              width: 100% !important;
              max-width: 100vw !important;
              box-sizing: border-box !important;
            }
            
            .quick-action-button {
              padding: 1rem !important;
              font-size: 0.95rem !important;
              min-height: 52px !important;
              width: 100% !important;
              border-radius: 4px !important;
            }
            
            .input-form {
              flex-direction: row !important;
              align-items: stretch !important;
              gap: 0.5rem !important;
              padding: 0 1rem !important;
              width: 100% !important;
              box-sizing: border-box !important;
            }
            
            .input-form > span:first-child {
              display: none !important;
            }
            
            .input-textarea {
              font-size: 1.1rem !important;
              padding: 0.75rem !important;
              border: 1px solid #444 !important;
              border-radius: 4px !important;
              background-color: #2a2a2a !important;
            }
            
            .flow-diagram {
              display: none !important;
            }
            
            button[type="submit"] {
              min-width: 80px !important;
              font-size: 0.95rem !important;
              border-radius: 4px !important;
              padding: 0.75rem 1rem !important;
            }
            
            /* Ensure no horizontal overflow */
            body {
              overflow-x: hidden !important;
            }
            
            #root {
              overflow-x: hidden !important;
              width: 100vw !important;
            }
          }
        `}
      </style>
      
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', width: '100%' }} className="container">
        {/* Main Terminal */}
        <div style={{ ...styles.terminal, flex: '1 1 auto', minHeight: 0, display: 'flex', flexDirection: 'column' }} className="terminal">
          {/* Header */}
          <div style={styles.header} className="terminal-header">
            <span style={{ color: '#ff6b35' }}>{isMobile ? 'ORÁCULO' : '🏛️ ORÁCULO DE LA BUROCRACIA'}</span>
            {messages.some(m => m.type === 'response') && (
              <button
                onClick={() => {
                  setMessages([
                    {
                      id: '1',
                      type: 'system',
                      content: getInitialGreeting(),
                      timestamp: new Date(),
                    },
                    {
                      id: '2',
                      type: 'system',
                      content: getInitialInstruction(),
                      timestamp: new Date(),
                    },
                  ]);
                  setShowFlow(true);
                  setCurrentFlow({ currentStep: 'idle' });
                        }}
                style={{
                  backgroundColor: 'transparent',
                  border: '1px solid #666',
                  color: '#999',
                  padding: '0.25rem 0.5rem',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  marginLeft: 'auto'
                }}
              >
                Limpiar
              </button>
            )}
          </div>

          {/* Flow Diagram - Show on load and during processing, hide when answer arrives */}
          {showFlow && (
            <div style={{ 
              padding: '1rem',
              borderBottom: '2px solid #444',
              flex: '2',  // Takes 2/3 of available space
              minHeight: 0,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }} className="flow-diagram">
              <FlowDiagramSimple flow={currentFlow} />
            </div>
          )}
          <div style={{
            ...styles.body,
            flex: showFlow ? '1' : '1',  // Always use flex: 1 to fill available space
            minHeight: 0,
            cursor: 'text'
          }} 
          ref={terminalRef} 
          className="terminal-body"
          onClick={(e) => {
            // Only focus input if clicking on the container itself, not on text
            if (e.target === e.currentTarget) {
              textareaRef.current?.focus();
            }
          }}>
            {messages
              .filter(message => {
                // When we have a response, only show user question and response
                const hasResponse = messages.some(m => m.type === 'response');
                if (hasResponse) {
                  return message.type === 'user' || message.type === 'response';
                }
                // Otherwise show all messages
                return true;
              })
              .map((message) => (
              <div key={message.id} style={{ marginBottom: '1rem', userSelect: 'text' }}>
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
                    <div style={{ whiteSpace: 'pre-wrap', userSelect: 'text', fontSize: '0.9rem' }}>{message.content}</div>
                    {(message.cost !== undefined || message.duration !== undefined) && (
                      <div style={{ color: '#999', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        {message.cost !== undefined && (
                          <div>💰 Costo: ${message.cost.toFixed(4)}</div>
                        )}
                        {message.duration !== undefined && (
                          <div>⏱️ Tiempo: {message.duration.toFixed(1)}s</div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            
            {/* Input Line - Only show if no responses */}
            {!messages.some(m => m.type === 'response') && (
              <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }} className="input-form">
                <span style={{ color: '#ff6b35', marginTop: '0.25rem' }}>&gt;</span>
                <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  adjustTextareaHeight();
                  // Don't change flow visibility while typing
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  } else if (e.key === 'Escape') {
                    e.preventDefault();
                    setInput('');
                    textareaRef.current?.blur();
                  }
                }}
                disabled={isProcessing}
                style={styles.input}
                className="input-textarea"
                placeholder={isProcessing ? getProcessingPlaceholder() : getInputPlaceholder()}
                rows={1}
                autoFocus
              />
              {!isProcessing && <span style={styles.cursor}></span>}
              <button
                type="submit"
                disabled={isProcessing || !input.trim()}
                style={{
                  ...styles.submitButton,
                  opacity: (isProcessing || !input.trim()) ? 0.5 : 1,
                  cursor: (isProcessing || !input.trim()) ? 'not-allowed' : 'pointer',
                }}
              >
                Enviar
              </button>
            </form>
            )}
          </div>
        </div>

        {/* Quick Actions - Only show if no responses */}
        {!messages.some(m => m.type === 'response') && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', 
            gap: '0.5rem', 
            marginTop: '1rem', 
            marginBottom: '1rem', 
            width: '100%',
            maxWidth: '600px', 
            flex: 'none' 
          }} className="quick-actions">
            {/* BCRA Only */}
            <button
              onClick={() => {
                setInput("¿Cuál es el límite para pagos al exterior?");
                textareaRef.current?.focus();
                setTimeout(adjustTextareaHeight, 0);
              }}
              style={styles.button}
              className="quick-action-button"
            >
              Límite Pagos (BCRA)
            </button>
            
            {/* COMEX Only */}
            <button
              onClick={() => {
                setInput("¿Cómo exportar vino a Brasil?");
                textareaRef.current?.focus();
                setTimeout(adjustTextareaHeight, 0);
              }}
              style={styles.button}
              className="quick-action-button"
            >
              Exportar Vino (COMEX)
            </button>
            
            {/* Show different buttons on mobile vs desktop */}
            {!isMobile && (
              <>
                {/* SENASA Only */}
                <button
                  onClick={() => {
                    setInput("¿Requisitos para exportar carne vacuna a China?");
                    textareaRef.current?.focus();
                    setTimeout(adjustTextareaHeight, 0);
                  }}
                  style={styles.button}
                  className="quick-action-button"
                >
                  Exportar Carne (SENASA)
                </button>
                
                {/* BCRA + COMEX */}
                <button
                  onClick={() => {
                    setInput("¿Cómo importar maquinaria industrial y pagar al proveedor?");
                    textareaRef.current?.focus();
                    setTimeout(adjustTextareaHeight, 0);
                  }}
                  style={styles.button}
                  className="quick-action-button"
                >
                  Importar y Pagar (BCRA+COMEX)
                </button>
                
                {/* COMEX + SENASA */}
                <button
                  onClick={() => {
                    setInput("¿Cómo exportar miel orgánica a la Unión Europea?");
                    textareaRef.current?.focus();
                    setTimeout(adjustTextareaHeight, 0);
                  }}
                  style={styles.button}
                  className="quick-action-button"
                >
                  Exportar Miel (COMEX+SENASA)
                </button>
                
                {/* All Three */}
                <button
                  onClick={() => {
                    setInput("¿Proceso completo para importar productos farmacéuticos?");
                    textareaRef.current?.focus();
                    setTimeout(adjustTextareaHeight, 0);
                  }}
                  style={styles.button}
                  className="quick-action-button"
                >
                  Importar Farma (TODOS)
                </button>
              </>
            )}
            
            {/* Mobile only shows most important question */}
            {isMobile && (
              <button
                onClick={() => {
                  setInput("¿Cómo importar maquinaria industrial y pagar al proveedor?");
                  textareaRef.current?.focus();
                  setTimeout(adjustTextareaHeight, 0);
                }}
                style={styles.button}
                className="quick-action-button"
              >
                Importar y Pagar
              </button>
            )}
          </div>
        )}

        {/* Copy Button - Only show when there's a response */}
        {messages.some(m => m.type === 'response') && (
          <div style={{ 
            marginTop: '1rem', 
            marginBottom: '1rem', 
            width: '100%',
            maxWidth: '600px', 
            display: 'flex',
            justifyContent: 'flex-start',
            flex: 'none' 
          }}>
            <button
              onClick={() => {
                const responseMessage = messages.find(m => m.type === 'response');
                if (responseMessage) {
                  navigator.clipboard.writeText(responseMessage.content).then(() => {
                    // Optional: Show a brief success indicator
                    const button = document.activeElement as HTMLButtonElement;
                    const originalText = button.textContent;
                    button.textContent = '✓ Copiado';
                    setTimeout(() => {
                      button.textContent = originalText;
                    }, 1000);
                  }).catch(err => {
                    console.error('Failed to copy text: ', err);
                  });
                }
              }}
              style={{
                ...styles.button,
                backgroundColor: '#2a2a2a',
                border: '2px solid #ff6b35',
                color: '#ff6b35',
                padding: '0.75rem 1.5rem',
                fontSize: '0.875rem',
                fontWeight: '600'
              }}
            >
              📋 Copiar Respuesta
            </button>
          </div>
        )}
      </div>
    </div>
  );
}