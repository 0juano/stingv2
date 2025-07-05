import React, { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import FlowDiagramSimple from './FlowDiagramSimple';
import QuestionScreen from './QuestionScreen';
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
  const [mobileScreen, setMobileScreen] = useState<'input' | 'processing' | 'result'>('input');
  const [lastResponse, setLastResponse] = useState<Message | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [copied, setCopied] = useState(false);
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
    console.log('[TerminalSimple] Form submitted with input:', input);
    
    if (!input.trim() || isProcessing) {
      console.log('[TerminalSimple] Submission blocked - empty input or already processing');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    console.log('[TerminalSimple] Creating user message:', userMessage);
    setMessages(prev => [...prev, userMessage]);
    setCurrentQuestion(input);  // Store the question for display during processing
    setInput('');
    setIsProcessing(true);
    
    // Mobile: transition to processing screen
    if (isMobile) {
      console.log('[TerminalSimple] Mobile detected - transitioning to processing screen');
      setMobileScreen('processing');
    }
    
    try {
      console.log('[TerminalSimple] Starting query processing...');
      setShowFlow(true);
      const result = await processQuery(input, (flow) => {
        console.log('[TerminalSimple] Flow update received:', flow);
        setCurrentFlow(flow);
        
        // Processing logs removed for simplified UI
      });

      console.log('[TerminalSimple] Query processing complete. Result:', result);
      
      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'response',
        content: result.response,
        timestamp: new Date(),
        flow: result.flow,
        cost: result.totalCost,
        duration: result.duration,
      };

      console.log('[TerminalSimple] Creating response message:', responseMessage);
      setMessages(prev => [...prev, responseMessage]);
      
      // Mobile: transition to result screen and store response
      if (isMobile) {
        console.log('[TerminalSimple] Mobile - transitioning to result screen');
        setLastResponse(responseMessage);
        setMobileScreen('result');
      }
      // Hide flow diagram immediately when response arrives
      setShowFlow(false);
    } catch (error: any) {
      console.error('[TerminalSimple] Error processing query:', error);
      console.error('[TerminalSimple] Error details:', {
        message: error.message,
        stack: error.stack,
        response: error.response?.data
      });
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      
      // Mobile: show error on result screen
      if (isMobile) {
        console.log('[TerminalSimple] Mobile - showing error on result screen');
        setLastResponse(errorMessage);
        setMobileScreen('result');
      }
    } finally {
      console.log('[TerminalSimple] Cleanup - resetting processing state');
      setIsProcessing(false);
      setCurrentFlow({ currentStep: 'idle' });
      // Keep flow hidden after processing
    }
  };

  const handleNewQuery = () => {
    // Reset everything for a new query
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
    setInput('');
    setCurrentQuestion('');  // Clear the stored question
    setCurrentFlow({ currentStep: 'idle' });
    setShowFlow(true);
    setMobileScreen('input');
    setLastResponse(null);
  };

  return (
    <div style={isMobile ? {} : styles.container} className="container">
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
          
          /* Retro terminal animations */
          @keyframes scanline {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
          }
          
          @keyframes terminalPrint {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          
          .scanline-transition {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: #00ff00;
            animation: scanline 0.5s ease-out;
            z-index: 9999;
          }
          
          .terminal-print {
            animation: terminalPrint 0.3s ease-out;
          }
          
          /* Prose styling for answer content */
          .prose {
            color: #e0e0e0;
          }
          
          .prose strong {
            font-weight: 600;
            color: #ffffff;
          }
          
          .answer-warning {
            background-color: rgba(107, 114, 128, 0.3);
            border-left: 4px solid #eab308;
            padding-left: 0.75rem;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            border-radius: 0.125rem;
            font-size: 0.875rem;
            margin: 0.75rem 0;
          }
          
          /* Mobile styles */
          @media (max-width: 768px) {
            .container {
              padding: 0 !important;
              margin: 0 !important;
              width: 100vw !important;
              height: 100vh !important;
              overflow-x: hidden !important;
              background-color: #0a0a0a !important;
              position: fixed !important;
              top: 0 !important;
              left: 0 !important;
              right: 0 !important;
              bottom: 0 !important;
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
            
            /* Mobile screen-specific styles */
            .mobile-input-screen {
              display: flex;
              flex-direction: column;
              height: 100vh;
              padding: 2rem 1.5rem;
              background-color: #1a1a1a;
            }
            
            .mobile-input-title {
              font-size: 1.75rem;
              font-weight: 600;
              color: #ff6b35;
              margin-bottom: 1rem;
              text-align: center;
              letter-spacing: 0.05em;
            }
            
            .mobile-input-container {
              flex: 1;
              display: flex;
              flex-direction: column;
              justify-content: center;
              gap: 1.5rem;
            }
            
            .mobile-input-field {
              width: 100%;
              padding: 1rem;
              font-size: 1.1rem;
              background-color: #2a2a2a;
              border: 2px solid #444;
              border-radius: 8px;
              color: #e0e0e0;
              font-family: inherit;
              min-height: 100px;
              resize: none;
            }
            
            .mobile-input-field:focus {
              border-color: #ff6b35;
              outline: none;
            }
            
            .mobile-submit-btn {
              padding: 1rem 2rem;
              font-size: 1.1rem;
              font-weight: 600;
              background-color: #2a2a2a;
              border: 2px solid #ff6b35;
              border-radius: 8px;
              color: #ff6b35;
              cursor: pointer;
            }
            
            .mobile-examples {
              display: flex;
              flex-direction: column;
              gap: 0.75rem;
              margin-top: 2rem;
              width: 100%;
            }
            
            .mobile-example-btn {
              padding: 1rem;
              font-size: 0.95rem;
              background-color: #1E1E1E;
              border: 1px solid rgba(156, 163, 175, 0.3);
              border-radius: 12px;
              color: #e0e0e0;
              cursor: pointer;
              text-align: left;
              transition: all 0.2s;
              font-family: inherit;
            }
            
            .mobile-example-btn:hover {
              background-color: #2a2a2a;
              border-color: #ff6b35;
              transform: translateY(-2px);
            }
            
            .mobile-processing-screen {
              position: fixed;
              top: 0;
              left: 0;
              width: 100vw;
              height: 100vh;
              background-color: #0a0a0a;
              display: flex;
              align-items: center;
              justify-content: center;
              z-index: 1000;
            }
            
            .mobile-result-screen {
              display: flex;
              flex-direction: column;
              height: 100vh;
              background-color: #1a1a1a;
            }
            
            .mobile-result-header {
              padding: 1.5rem 1.5rem 0.5rem 1.5rem;
              background-color: #0a0a0a;
              border-bottom: 1px solid #333;
              font-size: 1.1rem;
              font-weight: 600;
              color: #ff6b35;
            }
            
            .mobile-result-content {
              flex: 1;
              padding: 1.5rem;
              overflow-y: auto;
              font-size: 1rem;
              line-height: 1.6;
              color: #e0e0e0;
            }
            
            .mobile-result-actions {
              padding: 1rem 1rem 1rem 1rem;
              padding-bottom: env(safe-area-inset-bottom, 1rem);
              background-color: #0a0a0a;
              border-top: 1px solid #333;
              display: flex;
              gap: 0.5rem;
              position: relative;
            }
            
            .mobile-action-btn {
              flex: 1;
              padding: 0.875rem;
              font-size: 1rem;
              font-weight: 600;
              border-radius: 6px;
              cursor: pointer;
            }
            
            .mobile-action-primary {
              background-color: #2a2a2a;
              border: 2px solid #ff6b35;
              color: #ff6b35;
            }
            
            .mobile-action-secondary {
              background-color: #2a2a2a;
              border: 1px solid #666;
              color: #999;
            }
          }
        `}
      </style>
      
      {/* Mobile Experience - 3 Screens */}
      {isMobile && (
        <>
          {/* Screen 1: Input */}
          <AnimatePresence mode="wait">
            {mobileScreen === 'input' && (
              <QuestionScreen
                key="question-screen"
                onSubmit={async (question) => {
                  // Set the input and process the query directly
                  setInput(question);
                  setCurrentQuestion(question);  // Store the question for display
                  setIsProcessing(true);
                  setMobileScreen('processing');
                  
                  try {
                    console.log('[TerminalSimple] Processing question from QuestionScreen:', question);
                    setShowFlow(true);
                    const result = await processQuery(question, (flow) => {
                      console.log('[TerminalSimple] Flow update received:', flow);
                      setCurrentFlow(flow);
                    });

                    console.log('[TerminalSimple] Query processing complete. Result:', result);
                    
                    const responseMessage: Message = {
                      id: (Date.now() + 1).toString(),
                      type: 'response',
                      content: result.response,
                      timestamp: new Date(),
                      flow: result.flow,
                      cost: result.totalCost,
                      duration: result.duration,
                    };

                    setMessages(prev => [...prev, responseMessage]);
                    setLastResponse(responseMessage);
                    setMobileScreen('result');
                    setShowFlow(false);
                  } catch (error: any) {
                    console.error('[TerminalSimple] Error processing query:', error);
                    
                    const errorMessage: Message = {
                      id: (Date.now() + 1).toString(),
                      type: 'system',
                      content: `Error: ${error.message}`,
                      timestamp: new Date(),
                    };
                    setMessages(prev => [...prev, errorMessage]);
                    setLastResponse(errorMessage);
                    setMobileScreen('result');
                  } finally {
                    setIsProcessing(false);
                    setCurrentFlow({ currentStep: 'idle' });
                  }
                }}
                onExit={() => {}}
              />
            )}
          </AnimatePresence>
          
          {/* Screen 2: Processing */}
          <AnimatePresence>
            {mobileScreen === 'processing' && (
              <motion.div 
                className="mobile-processing-screen"
                initial={{ opacity: 0, y: 32 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  type: "spring",
                  duration: 0.2,
                  delay: 0.05
                }}
              >
                <div style={{ width: '100%', height: '100%', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
                  {/* Display the question at the top */}
                  {currentQuestion && (
                    <div style={{ 
                      textAlign: 'center', 
                      marginBottom: '1.5rem',
                      padding: '0 1rem',
                      color: '#e0e0e0',
                      fontSize: '1.1rem',
                      fontWeight: '500',
                      lineHeight: '1.4'
                    }}>
                      <div style={{ color: '#ff6b35', fontSize: '0.875rem', marginBottom: '0.5rem' }}>TU PREGUNTA:</div>
                      <div>{currentQuestion}</div>
                    </div>
                  )}
                  <FlowDiagramSimple flow={currentFlow} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Screen 3: Result */}
          {mobileScreen === 'result' && lastResponse && (
            <div className="mobile-result-screen terminal-print">
              <div className="mobile-result-header">RESPUESTA</div>
              <div className="mobile-result-content">
                <div style={{ whiteSpace: 'pre-wrap' }} className="text-xs">{lastResponse.content}</div>
                {(lastResponse.cost !== undefined || lastResponse.duration !== undefined) && (
                  <div className="grid grid-cols-2 gap-y-1 text-[11px] leading-tight mt-4 pt-4 border-t border-gray-700">
                    {lastResponse.cost !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-500">💰 Costo:</span>
                        <span className="ml-1">${lastResponse.cost.toFixed(4)}</span>
                      </div>
                    )}
                    {lastResponse.duration !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-500">⏱️ Tiempo:</span>
                        <span className="ml-1">{lastResponse.duration.toFixed(1)}s</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="mobile-result-actions relative">
                <button onClick={handleNewQuery} className="mobile-action-btn mobile-action-primary flex-1">
                  Nueva Consulta
                </button>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(lastResponse.content);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 1500);
                  }}
                  className="mobile-action-btn mobile-action-secondary flex-1"
                >
                  Copiar
                </button>
                {copied && (
                  <span className="absolute -top-8 inset-x-0 text-center text-xs text-emerald-400">
                    Texto copiado ✓
                  </span>
                )}
              </div>
            </div>
          )}
        </>
      )}
      
      {/* Desktop Experience - Keep unchanged */}
      {!isMobile && (
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
      )}
    </div>
  );
}