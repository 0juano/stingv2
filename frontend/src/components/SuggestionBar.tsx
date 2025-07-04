import { motion } from 'framer-motion';
import AssistChip from './AssistChip';

interface SuggestionBarProps {
  isVisible: boolean;
  keyboardHeight: number;
  onSelectExample: (text: string) => void;
}

const examples = [
  { icon: '📑', label: 'Límite pago exterior', text: '¿Cuál es el límite para pagos al exterior?' },
  { icon: '🍷', label: 'Exportar vino', text: '¿Cómo exportar vino a Brasil?' },
  { icon: '🏭', label: 'Importar maquinaria', text: '¿Cómo importar maquinaria industrial?' },
  { icon: '🥩', label: 'Exportar carne', text: '¿Requisitos para exportar carne vacuna?' },
];

/**
 * Suggestion bar that docks above the keyboard when input is focused
 * Always mounted but animated in/out of view
 */
export default function SuggestionBar({ isVisible, keyboardHeight, onSelectExample }: SuggestionBarProps) {
  // Respect reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <motion.div
      className="fixed left-0 right-0 bg-[#1a1a1a] border-t border-gray-700 z-50"
      style={{ bottom: keyboardHeight + 8 }}
      initial={{ y: '100%', opacity: 0 }}
      animate={isVisible ? { y: 0, opacity: 1 } : { y: '100%', opacity: 0 }}
      transition={
        prefersReducedMotion 
          ? { duration: 0.01 } 
          : { duration: 0.15, ease: 'easeOut' }
      }
      aria-hidden={!isVisible}
    >
      <div 
        className="py-3 px-4 overflow-x-auto whitespace-nowrap scrollbar-hide"
        style={{ WebkitOverflowScrolling: 'touch' }}
        role="group"
        aria-label="Example queries"
      >
        <div className="inline-flex gap-2">
          {examples.map((example, index) => (
            <AssistChip
              key={example.label}
              icon={example.icon}
              label={example.label}
              onClick={() => onSelectExample(example.text)}
              index={index}
              aria-label={`Use example: ${example.label}`}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}