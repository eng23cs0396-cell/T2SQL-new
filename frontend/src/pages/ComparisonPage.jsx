import React, { useState, useEffect } from 'react';
import { Layers, Play, Clock, ShieldCheck, AlertCircle, RefreshCw, Cpu, Zap, Database } from 'lucide-react';
import { listDatabases, compareModels, listAdapters } from '../services/api';
import SQLEditor from '../components/SQLEditor';
import DataTable from '../components/DataTable';

export default function ComparisonPage() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState('');
  const [question, setQuestion] = useState('Find the top 3 oldest students with their ages.');
  const [adapters, setAdapters] = useState([]);
  const [selectedAdapter, setSelectedAdapter] = useState('');
  const [comparing, setComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    listDatabases().then((res) => {
      setDatabases(res.data);
      if (res.data.length > 0) setSelectedDb(res.data[0].id);
    });
    listAdapters().then((res) => {
      setAdapters(res.data);
      if (res.data.length > 0) setSelectedAdapter(res.data[0].name);
    });
  }, []);

  const handleRunComparison = async () => {
    if (!selectedDb || !question.trim()) return;
    setComparing(true);
    setErrorMsg('');
    setComparisonResults(null);
    try {
      const res = await compareModels({
        database_id: selectedDb,
        question: question.trim(),
        num_few_shot_examples: 3,
        adapter_name: selectedAdapter || null,
      });
      setComparisonResults(res.data);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Comparison execution failed.');
    } finally {
      setComparing(false);
    }
  };

  const modelCards = comparisonResults
    ? [
        { key: 'nemotron', data: comparisonResults.models.nemotron, icon: Zap, color: 'cyan' },
        { key: 'qwen_few_shot', data: comparisonResults.models.qwen_few_shot, icon: Cpu, color: 'purple' },
        { key: 'qwen_lora', data: comparisonResults.models.qwen_lora, icon: Layers, color: 'indigo' },
      ]
    : [];

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
          <Layers className="w-7 h-7 text-cyan-400" />
          Model Architecture Comparison
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Execute a single database schema and question across all three approaches side-by-side to compare latency, SQL validity, and execution behavior.
        </p>
      </div>

      {/* Input Form Card */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1.5">
              Select Target Database
            </label>
            <select
              value={selectedDb}
              onChange={(e) => setSelectedDb(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            >
              {databases.map((db) => (
                <option key={db.id} value={db.id}>
                  {db.name}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1.5">
              Natural Language Question
            </label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter question to test across all three models..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
          <span className="text-xs text-slate-500 font-mono">
            Tests: Nemotron 3.5 Lightning (30B) &bull; Qwen2.5-Coder Few-Shot &bull; Qwen2.5-Coder LoRA
          </span>

          <button
            onClick={handleRunComparison}
            disabled={comparing || !question.trim()}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold shadow-lg shadow-indigo-500/20 hover:from-cyan-400 hover:to-indigo-500 transition-all disabled:opacity-50"
          >
            {comparing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running Comparison...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Comparison</span>
              </>
            )}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl border border-rose-900/60 bg-rose-950/20 text-xs text-rose-300 font-mono">
          <span className="font-bold text-rose-200">Error:</span> {errorMsg}
        </div>
      )}

      {/* Comparison Cards Grid */}
      {comparisonResults && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {modelCards.map(({ key, data, icon: Icon, color }) => {
            const hasError = !!data.error;
            return (
              <div
                key={key}
                className="rounded-2xl border border-slate-800 bg-[#0d1322] overflow-hidden shadow-xl flex flex-col justify-between"
              >
                {/* Header */}
                <div className="p-5 border-b border-slate-800 bg-slate-900/60 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <Icon className="w-4 h-4 text-cyan-400" />
                      {data.name}
                    </span>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-medium border ${
                        data.is_valid
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      }`}
                    >
                      {data.is_valid ? 'Valid SQL' : 'Invalid / Err'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                    <span className="text-slate-500 truncate max-w-[180px]">{data.technique}</span>
                    <span className="flex items-center gap-1 text-emerald-400">
                      <Clock className="w-3.5 h-3.5" />
                      {data.latency_ms} ms
                    </span>
                  </div>
                </div>

                {/* SQL Body */}
                <div className="p-4 flex-1 space-y-4">
                  <div>
                    <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                      Generated SQLite Query
                    </label>
                    <pre className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono text-emerald-300 whitespace-pre-wrap break-all min-h-[90px]">
                      {data.sql || <span className="text-slate-600 italic">No SQL generated</span>}
                    </pre>
                  </div>

                  {data.execution ? (
                    <div>
                      <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                        Execution Output ({data.execution.row_count} rows, {data.execution.execution_time_ms} ms)
                      </label>
                      <div className="overflow-x-auto max-h-[160px] border border-slate-800 rounded-lg bg-slate-950/60">
                        {data.execution.rows?.length === 0 ? (
                          <div className="p-3 text-xs text-slate-500 font-mono">0 rows returned.</div>
                        ) : (
                          <table className="w-full text-left text-xs font-mono">
                            <thead>
                              <tr className="bg-slate-900 border-b border-slate-800 text-slate-400">
                                {data.execution.columns?.map((c, i) => (
                                  <th key={i} className="py-1 px-2 text-cyan-400">
                                    {c}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {data.execution.rows?.slice(0, 5).map((r, ri) => (
                                <tr key={ri} className="border-b border-slate-800/40 text-slate-300">
                                  {r.map((v, ci) => (
                                    <td key={ci} className="py-1 px-2 whitespace-nowrap">
                                      {v === null ? 'NULL' : String(v)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                      </div>
                    </div>
                  ) : hasError ? (
                    <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-900/50 text-xs font-mono text-rose-300">
                      {data.error}
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

