import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Cpu,
  Database,
  Terminal,
  HardDrive,
  Activity,
  Layers,
  Save,
  ShieldCheck,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import {
  getFinetuningPreflight,
  listAdapters
} from '../services/api';

export default function FineTuningLabPage() {
  const [preflight, setPreflight] = useState(null);
  const [adapters, setAdapters] = useState([]);

  useEffect(() => {
    fetchPreflight();
    fetchAdapters();
    const interval = setInterval(fetchAdapters, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchPreflight = async () => {
    try {
      const res = await getFinetuningPreflight();
      setPreflight(res.data);
    } catch (err) {
      console.error('Error fetching preflight info:', err);
    }
  };

  const fetchAdapters = async () => {
    try {
      const res = await listAdapters();
      setAdapters(res.data);
    } catch (err) {
      console.error('Error fetching adapters:', err);
    }
  };

  // Fixed LoRA configuration specs for RTX 4060
  const loraRank = 8;
  const loraAlpha = 16;
  const loraDropout = 0.05;
  const approxTrainableParams = Math.round(loraRank * 4 * 2048 * 4 * 2); // ~4,194,304 params
  const approxTotalParams = 3090000000;
  const approxPct = ((approxTrainableParams / approxTotalParams) * 100).toFixed(4);

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
          <Sliders className="w-7 h-7 text-purple-400" />
          PEFT LoRA Fine-Tuning Console
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Architectural specification, parameter efficiency statistics, and adapter registry for Qwen2.5-Coder-3B-Instruct.
        </p>
      </div>

      {/* GPU & Hardware Assessment Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322] flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">Target Hardware</span>
            <span className="text-sm font-bold text-slate-200">
              {preflight?.device_name || 'NVIDIA RTX 4060 (8GB)'}
            </span>
            <span className="text-xs text-slate-500 block font-mono">
              VRAM: {preflight?.vram_gb || 8.0} GB Available
            </span>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322] flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <HardDrive className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">Base Checkpoint</span>
            <span className="text-sm font-bold text-slate-200">Qwen2.5-Coder-3B-Instruct</span>
            <span className="text-xs text-emerald-400 font-mono block">Base Weights Preserved (Frozen)</span>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322] flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">Supervised Dataset</span>
            <span className="text-sm font-bold text-slate-200">Spider Dataset (Yale LILY)</span>
            <span className="text-xs text-slate-500 font-mono block">2,000 Train &bull; 300 Val</span>
          </div>
        </div>
      </div>

      {/* Main Architecture & CLI Guide Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Configuration & Parameter Stats */}
        <div className="lg:col-span-5 p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-5">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              LoRA Configuration Specification
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Strictly tailored for NVIDIA RTX 4060 8GB VRAM envelope</p>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">LoRA Rank (r)</span>
                <span className="text-purple-400 font-bold text-sm">8</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Scaling Factor (α)</span>
                <span className="text-cyan-400 font-bold text-sm">16</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Batch Size / Accum</span>
                <span className="text-slate-200 font-bold text-sm">1 / 4 steps</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Seq Length</span>
                <span className="text-slate-200 font-bold text-sm">512 tokens</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px] uppercase mb-1">Target Linear Modules</span>
              <div className="flex gap-2 text-[11px]">
                {['q_proj', 'k_proj', 'v_proj', 'o_proj'].map((m) => (
                  <span key={m} className="px-2 py-0.5 rounded bg-slate-800 text-purple-300 border border-slate-700">
                    {m}
                  </span>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
              <span className="text-slate-400 text-[11px] uppercase tracking-wider block font-semibold">
                Parameter Efficiency Ratio
              </span>
              <div className="flex justify-between text-slate-300">
                <span>Trainable Parameters:</span>
                <span className="text-purple-400 font-bold">~{approxTrainableParams.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Total Parameters:</span>
                <span className="text-slate-400">3,090,000,000</span>
              </div>
              <div className="flex justify-between text-slate-300 border-t border-slate-800 pt-1">
                <span>Trainable Ratio:</span>
                <span className="text-emerald-400 font-bold">{approxPct}%</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/40 text-emerald-300 text-xs flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Base model checkpoint is never overwritten; adapters attach dynamically in PEFT mode.</span>
            </div>
          </div>
        </div>

        {/* Right: Terminal Execution Instructions & Saved Checkpoints */}
        <div className="lg:col-span-7 space-y-6">
          {/* CLI Execution Card */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <Terminal className="w-5 h-5 text-cyan-400" />
              <h3 className="font-bold text-white text-base">Terminal Training Execution</h3>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Fine-tuning is managed via dedicated command-line scripts to prevent long-running blocking operations in the browser and allow full inspection of GPU telemetry.
            </p>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-cyan-300 overflow-x-auto space-y-1">
              <div className="text-slate-500"># Run LoRA fine-tuning for Qwen2.5-Coder-3B:</div>
              <div className="select-all text-emerald-400 font-bold">
                .venv\Scripts\python.exe scripts/run_finetuning.py
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-400 space-y-1">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5 text-cyan-400" />
                Training Safeguards Applied
              </span>
              <ul className="list-disc list-inside text-slate-500 space-y-0.5 text-[11px]">
                <li>Gradient checkpointing enabled to keep peak memory inside 8GB VRAM</li>
                <li>FP16 mixed precision forward pass</li>
                <li>Instruction-masked labels (loss calculated only on target SQL tokens)</li>
              </ul>
            </div>
          </div>

          {/* Saved Adapters Registry */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Save className="w-4 h-4 text-emerald-400" />
                <h3 className="font-bold text-white text-sm">Registered LoRA Adapters</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">{adapters.length} Checkpoint(s)</span>
            </div>

            {adapters.length === 0 ? (
              <div className="p-6 rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-center space-y-2">
                <Sliders className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400 font-semibold">No adapter weights trained yet.</p>
                <p className="text-[11px] text-slate-500">
                  Run the CLI command above to train the rank-8 Spider adapter.
                </p>
              </div>
            ) : (
              <div className="space-y-2.5">
                {adapters.map((ad) => (
                  <div
                    key={ad.name}
                    className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/80 flex items-center justify-between text-xs font-mono"
                  >
                    <div>
                      <span className="font-bold text-slate-100">{ad.name}</span>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Rank: <span className="text-purple-400">{ad.rank}</span> &bull; Alpha: <span className="text-cyan-400">{ad.alpha}</span> &bull; Dropout: {ad.dropout}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-300 font-semibold">{ad.size_mb} MB</span>
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                        LOADABLE
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
