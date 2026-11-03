import React, { useState } from 'react';
import { Copy, Check, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function SQLEditor({ sql, validation, readOnly = false, onChange }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!sql) return;
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isValid = validation?.valid;

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d1322] overflow-hidden shadow-lg">
      {/* Editor Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-800 bg-slate-900/60">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-semibold tracking-wider uppercase text-cyan-400">
            Generated SQL
          </span>
          {validation && (
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                isValid
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
              }`}
            >
              {isValid ? (
                <>
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Valid SQL (Read-Only)</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Invalid Syntax</span>
                </>
              )}
            </span>
          )}
        </div>

        <button
          onClick={handleCopy}
          disabled={!sql}
          className="flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors disabled:opacity-50"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Editor Content Area */}
      <div className="p-4 font-mono text-sm leading-relaxed text-slate-200 overflow-x-auto min-h-[100px] flex">
        {readOnly ? (
          <pre className="w-full text-emerald-300 whitespace-pre-wrap break-all">
            {sql || <span className="text-slate-600 italic">-- Generated SQL query will appear here...</span>}
          </pre>
        ) : (
          <textarea
            value={sql || ''}
            onChange={(e) => onChange && onChange(e.target.value)}
            placeholder="-- Edit or write SQLite query here..."
            className="w-full bg-transparent resize-y text-emerald-300 focus:outline-none min-h-[90px] font-mono text-sm placeholder:text-slate-600"
          />
        )}
      </div>

      {/* Error detail if validation failed */}
      {!isValid && validation?.error && (
        <div className="px-4 py-2 bg-rose-950/30 border-t border-rose-900/50 text-xs text-rose-300 font-mono">
          <span className="font-semibold text-rose-200">Validation Error:</span> {validation.error}
        </div>
      )}
    </div>
  );
}

