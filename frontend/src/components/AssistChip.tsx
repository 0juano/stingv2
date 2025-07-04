import { motion } from 'framer-motion';

interface AssistChipProps {
  icon: string;
  label: string;
  onClick: () => void;
  index?: number;
  'aria-label'?: string;
}

export default function AssistChip({ 
  icon, 
  label, 
  onClick, 
  index = 0,
  'aria-label': ariaLabel 
}: AssistChipProps) {
  // Respect reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <motion.button
      onClick={onClick}
      role="button"
      aria-label={ariaLabel || `Use example: ${label}`}
      className="
        inline-flex items-center gap-2 py-3 px-4 min-w-[44px] min-h-[44px]
        bg-gray-800 border border-gray-600 rounded-full text-gray-300 text-sm
        whitespace-nowrap cursor-pointer transition-all duration-200
        hover:bg-gray-700 hover:border-gray-500 hover:text-white
      "
      initial={{ opacity: 0, y: prefersReducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: prefersReducedMotion ? 0 : 12 }}
      transition={{
        duration: prefersReducedMotion ? 0.01 : 0.15,
        delay: prefersReducedMotion ? 0 : index * 0.05,
        ease: 'easeOut'
      }}
      whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
    >
      <span className="text-base" aria-hidden="true">{icon}</span>
      <span>{label}</span>
    </motion.button>
  );
}