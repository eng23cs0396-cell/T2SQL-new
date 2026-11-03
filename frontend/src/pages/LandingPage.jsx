import React from 'react';
import {
  Sparkles,
  Database,
  Cpu,
  Layers,
  ArrowRight,
  ShieldCheck,
  Zap,
  GitBranch,
  Terminal,
  Activity,
  Sliders
} from 'lucide-react';

export default function LandingPage({ onStartQuerying, onExploreModels }) {
  const features = [
    {
      title: 'Dynamic Schema Extraction',
      description: 'Upload any SQLite database (.db, .sqlite). Tables, columns, primary keys, and foreign keys are introspected dynamically at runtime.',
      icon: Database,
      badge: 'Zero Hardcoding',
    },
    {
      title: 'NVIDIA Nemotron 3.5 Lightning',
      description: 'Ultra-fast API inference via NVIDIA NIM with internal thinking disabled for instant, production-grade SQL generation.',
      icon: Zap,
      badge: '30B MoE API',
    },
    {
      title: 'Local Qwen2.5-Coder-3B',
      description: 'Runs directly on your NVIDIA RTX 4060 GPU with 16-bit precision, offering complete data privacy and zero API dependence.',
      icon: Cpu,
      badge: 'Local GPU 8GB',
    },
    {
      title: 'Spider Few-Shot Prompting',
      description: 'In-context demonstration selection using curated Spider training exemplars covering JOINs, subqueries, and aggregates.',
      icon: Layers,
      badge: 'In-Context Learning',
    },
    {
      title: 'Supervised LoRA Fine-Tuning',
      description: 'Parameter-Efficient Fine-Tuning (PEFT) on Spider dataset. Freezes base weights and trains rank-8 adapters without overwriting checkpoints.',
      icon: Sliders,
      badge: 'PEFT / LoRA',
    },
    {
      title: 'LangChain & SQLGlot Guardrails',
      description: 'Orchestrated LangChain pipeline with AST parsing, schema table verification, and read-only URI mode execution authorizers.',
      icon: ShieldCheck,
      badge: 'Enterprise Security',
    },
  ];

  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="relative pt-12 pb-8 text-center max-w-4xl mx-auto px-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-400 mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Academic LLM Research Project – Dual Approach Text-to-SQL</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Intelligent Text-to-SQL <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-500">
            Comparative LLM Platform
          </span>
        </h1>

        <p className="text-lg text-slate-300 leading-relaxed max-w-2xl mx-auto mb-10 font-normal">
          Evaluate, benchmark, and compare high-throughput cloud inference with{' '}
          <span className="text-white font-semibold">NVIDIA Nemotron 3.5 Lightning</span> against local GPU inference with{' '}
          <span className="text-white font-semibold">Qwen2.5-Coder-3B-Instruct</span> across Few-Shot and LoRA fine-tuned paradigms.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={onStartQuerying}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold shadow-lg shadow-indigo-500/25 hover:from-cyan-400 hover:to-indigo-500 hover:shadow-cyan-500/20 hover:scale-[1.02] transition-all"
          >
            <Terminal className="w-4 h-4" />
            <span>Start Querying</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={onExploreModels}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700 font-medium transition-all"
          >
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Explore Models</span>
          </button>
        </div>
      </section>

      {/* Architecture Flow Diagram Card */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-2xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <GitBranch className="w-5 h-5 text-indigo-400" />
                LangChain Text-to-SQL Orchestration Flow
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">End-to-end execution path with mandatory schema & question inputs</p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              Verified Pipeline
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-center">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center">
              <Database className="w-6 h-6 text-cyan-400 mb-2" />
              <span className="text-xs font-bold text-slate-200">User SQLite DB</span>
              <span className="text-[11px] text-slate-500 mt-1">PRAGMA introspection</span>
            </div>

            <div className="flex items-center justify-center text-slate-600 font-mono text-xl hidden md:flex">
              →
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-indigo-900/40 flex flex-col items-center justify-center">
              <Layers className="w-6 h-6 text-indigo-400 mb-2" />
              <span className="text-xs font-bold text-slate-200">Schema + Question</span>
              <span className="text-[11px] text-slate-500 mt-1">Dynamic Prompt Assembly</span>
            </div>

            <div className="flex items-center justify-center text-slate-600 font-mono text-xl hidden md:flex">
              →
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-purple-900/40 flex flex-col items-center justify-center">
              <Cpu className="w-6 h-6 text-purple-400 mb-2" />
              <span className="text-xs font-bold text-slate-200">Dual Model Engine</span>
              <span className="text-[11px] text-slate-500 mt-1">Nemotron / Qwen LoRA</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">Core Research Capabilities</h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Built from scratch to systematically demonstrate and compare the trade-offs of API reasoning models versus fine-tuned local small language models.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-xl border border-slate-800 bg-[#0d1322] hover:border-slate-700 transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:text-cyan-400 group-hover:border-cyan-500/30 transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                    {feat.badge}
                  </span>
                </div>
                <h3 className="font-semibold text-slate-200 text-base mb-2">{feat.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{feat.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-4 pt-12 border-t border-slate-800/80 text-center text-xs text-slate-500 font-mono">
        QueryMind Platform &bull; Academic Text-to-SQL LLM Evaluation Suite &bull; PyTorch + Hugging Face PEFT + FastAPI + React
      </footer>
    </div>
  );
}

