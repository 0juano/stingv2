import { motion } from 'framer-motion';
import AssistChip from './AssistChip';

interface SuggestionBarProps {
  onSelectExample: (text: string) => void;
  keyboardHeight?: number;
}

// Fixed 4 example chips as specified
const examples = [
  {
    label: "Límite Pagos (BCRA)",
    query: "¿Cuál es el límite para pagos al exterior?",
    agents: ["BCRA"]
  },
  {
    label: "Exportar Vino (COMEX)",
    query: "¿Cómo exportar vino a Brasil?",
    agents: ["COMEX"]
  },
  {
    label: "Exportar Miel (COMEX+SENASA)",
    query: "¿Qué requisitos para exportar miel?",
    agents: ["COMEX", "SENASA"]
  },
  {
    label: "Importar Farma (TODOS)",
    query: "¿Cómo importar productos farmacéuticos?",
    agents: ["TODOS"]
  }
];

export default function SuggestionBar({ onSelectExample }: SuggestionBarProps) {
  return (
    <motion.div 
      className="flex gap-2 overflow-x-auto whitespace-nowrap scrollbar-hide pb-2"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      {examples.map((example, index) => (
        <motion.div
          key={example.label}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 + index * 0.05 }}
        >
          <AssistChip
            label={example.label}
            query={example.query}
            agents={example.agents}
            onClick={onSelectExample}
          />
        </motion.div>
      ))}
    </motion.div>
  );
}