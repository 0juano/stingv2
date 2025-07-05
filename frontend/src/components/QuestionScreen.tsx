import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import SuggestionBar from './SuggestionBar';
import { ExampleGrid } from './ExampleGrid';
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
    // Set input and immediately submit (skip shake animation)
    setInput(text);
    setError('');
    setIsLoading(true);
    
    // Blur input and trigger submit
    inputRef.current?.blur();
    if (onExit) onExit();
    setTimeout(() => onSubmit(text), 150);
  };

  return (
    <motion.div 
      className="min-h-dvh flex flex-col justify-between px-6 bg-[#0a0a0a] text-white md:max-w-xs md:mx-auto md:px-0 md:bg-transparent"
      initial={{ opacity: 0, y: 32 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -32 }}
      transition={{ 
        type: "spring",
        duration: 0.4,
        delay: 0.05
      }}
    >
      {/* Header */}
      <header className="pt-8 pb-6 text-center space-y-2">
        <h1 className="text-2xl md:text-3xl font-extrabold">
          <span className="text-orange-500">ORACULO DE BUROCRACIA</span>
        </h1>
        <p className="text-xs text-gray-400">Tu guía en regulaciones argentinas</p>
      </header>

      {/* Form section */}
      <div>
        <form onSubmit={handleSubmit} className="w-full space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              ¿Cuál es tu consulta?
            </label>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Ej: ¿Cómo exportar vino?"
              disabled={isLoading}
              className={`w-full px-4 py-3 text-base bg-[#1a1a1a] border rounded-lg placeholder-gray-500 transition-all duration-200 text-ellipsis focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500 disabled:opacity-50 ${isShaking ? 'animate-shake' : ''} ${isFocused ? 'border-orange-500' : 'border-gray-700'}`}
              style={{
                borderColor: error ? '#ef4444' : undefined
              }}
            />
            {error && (
              <motion.p 
                className="text-xs text-red-400"
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {error}
              </motion.p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-6 text-base font-semibold rounded-lg transition-all duration-200 transform bg-orange-600 hover:bg-orange-700 hover:scale-[1.02] active:scale-[0.98] disabled:bg-gray-700 disabled:scale-100 focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Procesando...
              </span>
            ) : (
              'Consultar'
            )}
          </button>
        </form>
      </div>

      {/* Adaptive spacer - grows only when space available */}
      <div className="flex-1 max-h-8" />

      {/* Grid examples section */}
      <div className="pb-6" style={{ paddingBottom: keyboardHeight > 0 ? keyboardHeight + 24 : 24 }}>
        {/* Mobile grid - visible on small screens */}
        <motion.div 
          className="block md:hidden"
          layout
          transition={{ duration: 0.2 }}
        >
          <ExampleGrid onSelect={handleSelectExample} />
        </motion.div>
        
        {/* Desktop chips - visible on medium screens and up */}
        <div className="hidden md:block space-y-2">
          <p className="text-sm text-gray-400">O selecciona una consulta frecuente:</p>
          <SuggestionBar 
            onSelectExample={handleSelectExample} 
            keyboardHeight={keyboardHeight}
          />
        </div>
      </div>
    </motion.div>
  );
}