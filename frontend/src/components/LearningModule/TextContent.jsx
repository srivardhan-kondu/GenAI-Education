import React from 'react'

export default function TextContent({ definition, explanation, examples, keyPoints, summary }) {
  return (
    <div className="space-y-6 animate-fade-in">

      {/* Definition */}
      <div className="card border-l-4 border-indigo-500">
        <h2 className="text-lg font-bold text-slate-800 mb-2 flex items-center gap-2">
          📌 Definition
        </h2>
        <p className="text-slate-700 leading-relaxed">{definition}</p>
      </div>

      {/* Explanation */}
      <div className="card">
        <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
          💡 Explanation
        </h2>
        <p className="text-slate-700 leading-relaxed whitespace-pre-line">{explanation}</p>
      </div>

      {/* Key Points */}
      {keyPoints?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
            🔑 Key Points
          </h2>
          <ul className="space-y-2">
            {keyPoints.map((point, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="mt-0.5 flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                <span className="text-slate-700 text-sm leading-relaxed">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Examples */}
      {examples?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
            📝 Examples
          </h2>
          <div className="space-y-3">
            {examples.map((ex, i) => (
              <div key={i} className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
                <span className="text-amber-600 font-bold text-sm">#{i + 1}</span>
                <p className="text-slate-700 text-sm leading-relaxed">{ex}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="card bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-100">
          <h2 className="text-lg font-bold text-slate-800 mb-2 flex items-center gap-2">
            📋 Summary
          </h2>
          <p className="text-slate-700 leading-relaxed">{summary}</p>
        </div>
      )}
    </div>
  )
}
