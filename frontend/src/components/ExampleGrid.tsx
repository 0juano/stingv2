interface Example {
  word: string;
  query: string;
  agents: string[];
}

const EXAMPLES: Example[] = [
  { word: "Pagos", query: "¿Cuál es el límite para pagos al exterior?", agents: ["BCRA"] },
  { word: "Vino",  query: "¿Cómo exportar vino a Brasil?",             agents: ["COMEX"] },
  { word: "Miel",  query: "¿Qué requisitos para exportar miel?",       agents: ["COMEX", "SENASA"] },
  { word: "Farma", query: "¿Cómo importar productos farmacéuticos?",   agents: ["BCRA", "COMEX", "SENASA"] },
];

interface ExampleGridProps {
  onSelect: (query: string) => void;
}

export function ExampleGrid({ onSelect }: ExampleGridProps) {
  return (
    <div
      className="grid grid-cols-2 gap-4 w-full"
      role="list"
    >
      {EXAMPLES.map(ex => (
        <button
          key={ex.word}
          role="listitem"
          aria-label={`Usar ejemplo ${ex.word}`}
          className="flex flex-col items-center justify-center gap-1 h-16 rounded-lg bg-[#1E1E1E]/70
                     text-xs font-medium border border-gray-800 hover:border-orange-500/50
                     hover:bg-[#222] active:bg-[#2a2a2a] transition-all duration-200
                     focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 
                     focus-visible:outline-orange-500"
          onClick={() => onSelect(ex.query)}
        >
          <span className="text-sm font-bold text-gray-100">{ex.word}</span>
          <span className="text-[10px] text-gray-400">
            {ex.agents.length === 3 ? "TODOS" : ex.agents.join(" + ")}
          </span>
        </button>
      ))}
    </div>
  );
}