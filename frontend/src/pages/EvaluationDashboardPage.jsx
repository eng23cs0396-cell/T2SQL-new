import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Play,
  Download,
  CheckCircle,
  AlertTriangle,
  Clock,
  Layers,
  RefreshCw,
  Cpu,
  Zap,
  ShieldCheck,
  FileText
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  getLatestEvaluationResults,
  runEvaluation,
  getEvaluationStatus,
  getExportUrl
} from '../services/api';

export default function EvaluationDashboardPage() {
  const [evalResults, setEvalResults] = useState({});
  const [selectedModel, setSelectedModel] = useState('nemotron');
  const [testLimit, setTestLimit] = useState(10);
  const [runningJobId, setRunningJobId] = useState(null);
  const [jobState, setJobState] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const res = await getLatestEvaluationResults();
      setEvalResults(res.data || {});
    } catch (err) {
      console.error('Error fetching evaluation results:', err);
    }
  };

  // Poll running evaluation job
  useEffect(() => {
    if (!runningJobId) return;
    const interval = setInterval(async () => {
      try {
        const res = await getEvaluationStatus(runningJobId);
        setJobState(res.data);
        if (res.data.status === 'COMPLETED' || res.data.status === 'FAILED') {
          clearInterval(interval);
          setRunningJobId(null);
          fetchResults();
        }
      } catch (err) {
        console.error('Error polling evaluation status:', err);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [runningJobId]);

  const handleStartEvaluation = async () => {
    setErrorMsg('');
    try {
      const res = await runEvaluation({
        model_type: selectedModel,
        test_limit: Number(testLimit),
      });
      setRunningJobId(res.data.job_id);
      setJobState({ status: 'RUNNING' });
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to trigger evaluation run.');
    }
  };

  // Prepare chart data from real evaluation metrics
  const modelsWithResults = Object.keys(evalResults);
  const chartData = modelsWithResults.map((key) => {
    const data = evalResults[key];
    const nameMap = {
      nemotron: 'Nemotron 3.5 Lightning',
      qwen_few_shot: 'Qwen Few-Shot',
      qwen_lora: 'Qwen LoRA',
    };
    return {
      modelKey: key,
      name: nameMap[key] || key,
      accuracy: data.execution_accuracy,
      validity: data.sql_validity_rate,
      latency: data.avg_generation_time_ms,
    };
  });

  // Pick detailed table from first available model or selected
  const activeDetailedModel = evalResults[selectedModel] || (modelsWithResults.length > 0 ? evalResults[modelsWithResults[0]] : null);

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
            <BarChart3 className="w-7 h-7 text-cyan-400" />
            Common Evaluation Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Empirical benchmarking on held-out Spider test instances. Real execution accuracy, validity rates, and latency.
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          <a
            href={getExportUrl('csv')}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export CSV</span>
          </a>
          <a
            href={getExportUrl('json')}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all"
          >
            <FileText className="w-3.5 h-3.5 text-purple-400" />
            <span>Export JSON</span>
          </a>
        </div>
      </div>

      {/* Benchmark Control Bar */}
      <div className="p-5 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4 text-xs font-semibold">
          <div>
            <span className="text-slate-400 uppercase tracking-wider block mb-1">Evaluate Model</span>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 font-mono"
            >
              <option value="nemotron">NVIDIA Nemotron 3.5 Lightning</option>
              <option value="qwen_few_shot">Local Qwen (Few-Shot Prompting)</option>
              <option value="qwen_lora">Local Qwen (LoRA Fine-Tuned)</option>
            </select>
          </div>

          <div>
            <span className="text-slate-400 uppercase tracking-wider block mb-1">Held-Out Questions</span>
            <select
              value={testLimit}
              onChange={(e) => setTestLimit(Number(e.target.value))}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 font-mono"
            >
              <option value={5}>5 Questions (Fast Benchmark)</option>
              <option value={10}>10 Questions</option>
              <option value={20}>20 Questions (Comprehensive)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleStartEvaluation}
          disabled={runningJobId !== null}
          className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold shadow-lg shadow-indigo-500/20 hover:from-cyan-400 hover:to-indigo-500 transition-all disabled:opacity-50"
        >
          {runningJobId ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Benchmarking in Background...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Run Evaluation Benchmark</span>
            </>
          )}
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl border border-rose-900/60 bg-rose-950/20 text-xs text-rose-300 font-mono">
          {errorMsg}
        </div>
      )}

      {/* Empty State vs Real Metrics Display */}
      {modelsWithResults.length === 0 ? (
        <div className="p-12 rounded-2xl border border-dashed border-slate-800 bg-[#0d1322]/50 text-center space-y-3">
          <BarChart3 className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="font-bold text-slate-300 text-base">No Evaluation Experiments Recorded Yet</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Click &ldquo;Run Evaluation Benchmark&rdquo; above to execute held-out Spider test cases against the selected model architecture.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Top Execution Accuracy
              </span>
              <span className="text-2xl font-extrabold text-cyan-400 font-mono mt-1 block">
                {Math.max(...chartData.map((d) => d.accuracy))}%
              </span>
              <span className="text-[11px] text-slate-500 mt-1 block">Semantic multiset match</span>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Top SQL Validity Rate
              </span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono mt-1 block">
                {Math.max(...chartData.map((d) => d.validity))}%
              </span>
              <span className="text-[11px] text-slate-500 mt-1 block">SQLGlot AST verified</span>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Fastest Avg Latency
              </span>
              <span className="text-2xl font-extrabold text-purple-400 font-mono mt-1 block">
                {Math.min(...chartData.map((d) => d.latency))} ms
              </span>
              <span className="text-[11px] text-slate-500 mt-1 block">Per question generation</span>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Models Evaluated
              </span>
              <span className="text-2xl font-extrabold text-white font-mono mt-1 block">
                {modelsWithResults.length} / 3
              </span>
              <span className="text-[11px] text-slate-500 mt-1 block">Dual approach coverage</span>
            </div>
          </div>

          {/* Interactive Recharts Comparison Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart 1: Execution Accuracy & Validity */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-3">
              <h3 className="font-bold text-white text-sm">Execution Accuracy vs SQL Validity (%)</h3>
              <div className="h-[260px] w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Bar dataKey="accuracy" name="Execution Accuracy (%)" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="validity" name="SQL Validity Rate (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Generation Latency */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-3">
              <h3 className="font-bold text-white text-sm">Average Inference Latency (ms)</h3>
              <div className="h-[260px] w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Bar dataKey="latency" name="Average Latency (ms)" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Detailed Per-Question Results Table */}
          {activeDetailedModel && (
            <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  Detailed Test Case Results ({activeDetailedModel.model_type})
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  {activeDetailedModel.detailed_results?.length || 0} Test Instances
                </span>
              </div>

              <div className="overflow-x-auto max-h-[380px]">
                <table className="w-full text-left text-xs font-mono border-collapse">
                  <thead>
                    <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 sticky top-0">
                      <th className="py-2.5 px-3">Database</th>
                      <th className="py-2.5 px-3">Question</th>
                      <th className="py-2.5 px-3">Gold SQL</th>
                      <th className="py-2.5 px-3">Predicted SQL</th>
                      <th className="py-2.5 px-3 text-center">Accuracy</th>
                      <th className="py-2.5 px-3 text-right">Latency</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {activeDetailedModel.detailed_results?.map((caseItem, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-2 px-3 text-cyan-400 font-semibold">{caseItem.db_id}</td>
                        <td className="py-2 px-3 text-slate-200 max-w-[220px] truncate">{caseItem.question}</td>
                        <td className="py-2 px-3 text-slate-400 max-w-[200px] truncate">{caseItem.gold_sql}</td>
                        <td className="py-2 px-3 text-emerald-300 max-w-[200px] truncate">{caseItem.predicted_sql}</td>
                        <td className="py-2 px-3 text-center">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              caseItem.execution_accuracy
                                ? 'bg-emerald-500/10 text-emerald-400'
                                : 'bg-rose-500/10 text-rose-400'
                            }`}
                          >
                            {caseItem.execution_accuracy ? 'CORRECT' : 'INCORRECT'}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-right text-slate-400">{caseItem.latency_ms} ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

