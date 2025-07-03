import { useState } from 'react';

interface ConfidenceBreakdown {
  base: { achieved: number; possible: number };
  specific_regulations: { achieved: number; possible: number };
  exact_articles: { achieved: number; possible: number };
  complete_procedures: { achieved: number; possible: number };
  recent_updates: { achieved: number; possible: number };
}

interface ConfidenceTooltipProps {
  score: number;
  breakdown: ConfidenceBreakdown;
}

export function ConfidenceTooltip({ score, breakdown }: ConfidenceTooltipProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const getCheckMark = (achieved: number, possible: number) => {
    return achieved === possible ? '✓' : '✗';
  };

  const getColor = (achieved: number, possible: number) => {
    return achieved === possible ? 'text-green-500' : 'text-red-500';
  };

  return (
    <span 
      className="relative inline-block"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span className="text-blue-600 underline cursor-help italic">
        Confianza: {score}%
      </span>
      
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50">
          <div className="bg-gray-900 text-white p-4 rounded-lg shadow-xl border border-gray-700 whitespace-nowrap">
            <div className="text-sm font-bold mb-2 text-center">Confidence Score Breakdown:</div>
            <div className="border-t border-gray-600 pt-2">
              <table className="text-xs font-mono">
                <tbody>
                  <tr>
                    <td className="pr-4">Base score:</td>
                    <td className="text-right pr-2">{breakdown.base.achieved}</td>
                    <td>/</td>
                    <td className="pl-1">{breakdown.base.possible}</td>
                    <td className={`pl-2 ${getColor(breakdown.base.achieved, breakdown.base.possible)}`}>
                      {getCheckMark(breakdown.base.achieved, breakdown.base.possible)}
                    </td>
                  </tr>
                  <tr>
                    <td className="pr-4">Specific regulations:</td>
                    <td className="text-right pr-2">{breakdown.specific_regulations.achieved}</td>
                    <td>/</td>
                    <td className="pl-1">{breakdown.specific_regulations.possible}</td>
                    <td className={`pl-2 ${getColor(breakdown.specific_regulations.achieved, breakdown.specific_regulations.possible)}`}>
                      {getCheckMark(breakdown.specific_regulations.achieved, breakdown.specific_regulations.possible)}
                    </td>
                  </tr>
                  <tr>
                    <td className="pr-4">Exact articles:</td>
                    <td className="text-right pr-2">{breakdown.exact_articles.achieved}</td>
                    <td>/</td>
                    <td className="pl-1">{breakdown.exact_articles.possible}</td>
                    <td className={`pl-2 ${getColor(breakdown.exact_articles.achieved, breakdown.exact_articles.possible)}`}>
                      {getCheckMark(breakdown.exact_articles.achieved, breakdown.exact_articles.possible)}
                    </td>
                  </tr>
                  <tr>
                    <td className="pr-4">Complete procedures:</td>
                    <td className="text-right pr-2">{breakdown.complete_procedures.achieved}</td>
                    <td>/</td>
                    <td className="pl-1">{breakdown.complete_procedures.possible}</td>
                    <td className={`pl-2 ${getColor(breakdown.complete_procedures.achieved, breakdown.complete_procedures.possible)}`}>
                      {getCheckMark(breakdown.complete_procedures.achieved, breakdown.complete_procedures.possible)}
                    </td>
                  </tr>
                  <tr>
                    <td className="pr-4">Recent updates:</td>
                    <td className="text-right pr-2">{breakdown.recent_updates.achieved}</td>
                    <td>/</td>
                    <td className="pl-1">{breakdown.recent_updates.possible}</td>
                    <td className={`pl-2 ${getColor(breakdown.recent_updates.achieved, breakdown.recent_updates.possible)}`}>
                      {getCheckMark(breakdown.recent_updates.achieved, breakdown.recent_updates.possible)}
                    </td>
                  </tr>
                </tbody>
              </table>
              <div className="border-t border-gray-600 mt-2 pt-2">
                <table className="text-xs font-mono w-full">
                  <tbody>
                    <tr>
                      <td className="pr-4 font-bold">Total:</td>
                      <td className="text-right pr-2 font-bold">{score}</td>
                      <td className="font-bold">/</td>
                      <td className="pl-1 font-bold">100</td>
                      <td className="pl-2"></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-2">
            <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      )}
    </span>
  );
}