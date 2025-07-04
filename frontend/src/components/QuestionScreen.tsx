import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import SuggestionBar from './SuggestionBar';
import { useKeyboardHeight } from '../hooks/useKeyboardHeight';

interface QuestionScreenProps {
  onSubmit: (question: string) => void;
  onExit?: () => void;
}

export default function QuestionScreen({ onSubmit, onExit }: QuestionScreenProps) {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isShaking, setIsShaking] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const keyboardHeight = useKeyboardHeight();

  // Auto-focus on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) {
      setError('Por favor ingrese una pregunta para continuar');
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 300);
      return;
    }

    setIsLoading(true);
    setError('');
    inputRef.current?.blur();
    
    // Trigger exit animation and submit
    if (onExit) onExit();
    setTimeout(() => onSubmit(input), 150);
  };

  const handleSelectExample = (text: string) => {
    setInput(text);
    setError('');
    // Focus input to show updated text
    inputRef.current?.focus();
  };

  // Respect reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <motion.div
      className="min-h-dvh flex flex-col bg-[#1a1a1a] text-[#e0e0e0] fixed inset-0 w-full h-full md:relative md:inset-auto"
      initial={{ opacity: 1, scale: 1 }}
      exit={prefersReducedMotion 
        ? { opacity: 0 } 
        : { opacity: 0, scale: 0.96 }
      }
      transition={{ duration: 0.15, ease: 'easeInOut' }}
    >
      {/* Pinned header block */}
      <header className="h-28 sticky top-0 bg-[#1a1a1a] flex flex-col items-center justify-center px-6 z-10 md:relative md:bg-transparent">
        <h1 className="text-2xl font-bold text-[#ff6b35] text-center mb-2 tracking-wider">
          ORÁCULO DE LA BUROCRACIA
        </h1>
        <p className="text-gray-400 text-center text-sm">
          ¿Qué trámite necesitás resolver hoy?
        </p>
      </header>

      {/* Main content area with input */}
      <div className="flex-1 flex flex-col items-center px-6">
        <form onSubmit={handleSubmit} className="w-full max-w-xs mt-4">
          <div className={`relative ${isShaking ? 'animate-shake' : ''}`}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                setError('');
              }}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder='Ej: "Límite pago exterior" | "Exportar vino"'
              aria-label="User question"
              aria-describedby="examplesHint"
              aria-invalid={!!error}
              className={`
                border bg-[#1E1E1E] rounded-md px-4 py-2 w-full text-white text-base
                outline-none transition-colors duration-200
                ${isFocused ? 'border-[#ff6b35]' : 'border-gray-400/60 hover:border-gray-400/80'}
              `}
            />
            
            {/* Error message */}
            {error && (
              <p
                className="text-red-500 text-xs mt-1 absolute"
                role="alert"
              >
                {error}
              </p>
            )}
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`
              mt-4 w-full py-3 px-6 rounded-lg font-semibold text-base
              border-2 border-[#ff6b35] text-[#ff6b35]
              transition-all duration-200
              ${input.trim() && !isLoading 
                ? 'opacity-100 cursor-pointer hover:bg-[#ff6b35] hover:text-black' 
                : 'opacity-40 cursor-not-allowed'
              }
            `}
          >
            {isLoading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Procesando...
              </span>
            ) : (
              'ENVIAR'
            )}
          </button>
        </form>

        {/* Hidden hint for screen readers */}
        <p id="examplesHint" className="sr-only">
          Example queries available below when input is focused
        </p>
      </div>

      {/* Suggestion bar - always mounted */}
      <SuggestionBar
        isVisible={isFocused}
        keyboardHeight={keyboardHeight}
        onSelectExample={handleSelectExample}
      />
    </motion.div>
  );
}