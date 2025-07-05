
interface AssistChipProps {
  label: string;
  query: string;
  agents: string[];
  onClick: (query: string) => void;
}

export default function AssistChip({ label, query, agents, onClick }: AssistChipProps) {
  // Icon mapping for agents
  const iconMap: Record<string, string> = {
    BCRA: "💰",
    COMEX: "📦", 
    SENASA: "🌱",
    TODOS: "🤝"
  };

  // Get the first icon from agents array
  const icon = agents.includes("TODOS") ? iconMap.TODOS : iconMap[agents[0]];

  return (
    <button
      onClick={() => onClick(query)}
      role="button"
      aria-label={`Usar ejemplo: ${label}`}
      className="
        inline-flex items-center gap-2 px-3 py-2
        bg-[#1a1a1a] hover:bg-[#222] active:bg-[#2a2a2a]
        border border-gray-700 hover:border-orange-500/50
        rounded-full whitespace-nowrap
        text-xs text-gray-300 hover:text-white
        transition-all duration-200
        transform hover:scale-[1.02] active:scale-[0.98]
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500
        min-h-[36px]
      "
    >
      {icon && <span className="text-base">{icon}</span>}
      <span>{label}</span>
    </button>
  );
}