import React from 'react';
import { Clock, Table as TableIcon, AlertCircle } from 'lucide-react';

export default function DataTable({ executionResult, loading }) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 border border-slate-800 rounded-xl bg-[#0d1322]">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-sm text-slate-400 font-mono">Executing query against SQLite database...</p>
      </div>
    );
  }

  if (!executionResult) {
    return (
      <div className="flex flex-col items-center justify-center py-14 border border-dashed border-slate-800 rounded-xl bg-[#090d16]/50 text-center">
        <TableIcon className="w-10 h-10 text-slate-600 mb-2" />
        <p className="text-sm text-slate-400">No query executed yet.</p>
        <p className="text-xs text-slate-600 mt-1">Generate and click "Execute Query" to inspect database results.</p>
      </div>
    );
  }

  const { success, columns = [], rows = [], row_count = 0, execution_time_ms = 0, error, truncated } = executionResult;

  if (!success) {
    return (
      <div className="p-4 rounded-xl border border-rose-900/60 bg-rose-950/20 text-rose-300">
        <div className="flex items-center gap-2 font-semibold text-sm mb-1 text-rose-200">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <span>SQL Execution Failed</span>
        </div>
        <p className="text-xs font-mono whitespace-pre-wrap">{error || 'Unknown execution error occurred.'}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d1322] overflow-hidden shadow-lg">
      {/* Table Header Details */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900/70 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-200">Query Results</span>
          <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
            {row_count} {row_count === 1 ? 'row' : 'rows'}
          </span>
          {truncated && (
            <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
              Truncated at 100 rows
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5 text-slate-400 font-mono">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{execution_time_ms} ms</span>
        </div>
      </div>

      {/* Tabular Data Grid */}
      <div className="overflow-x-auto max-h-[360px]">
        {rows.length === 0 ? (
          <div className="py-8 text-center text-sm text-slate-500 font-mono">
            Query returned 0 records.
          </div>
        ) : (
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-300 sticky top-0 z-10">
                <th className="py-2.5 px-3 w-10 text-slate-600 border-r border-slate-800/60 text-center">#</th>
                {columns.map((col, idx) => (
                  <th key={idx} className="py-2.5 px-3 font-semibold tracking-wider text-cyan-300">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {rows.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2 px-3 text-slate-600 text-center border-r border-slate-800/40">
                    {rIdx + 1}
                  </td>
                  {row.map((val, cIdx) => (
                    <td key={cIdx} className="py-2 px-3 text-slate-300 whitespace-nowrap">
                      {val === null ? (
                        <span className="text-slate-600 italic">NULL</span>
                      ) : typeof val === 'number' ? (
                        <span className="text-amber-300">{val}</span>
                      ) : (
                        String(val)
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

