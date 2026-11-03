import React, { useEffect, useState } from 'react';
import { Database, Cpu, Activity, Sparkles, Layers, Sliders, BarChart3, Terminal } from 'lucide-react';
import { getHealth } from '../services/api';

export default function Navbar({ activeTab, setActiveTab }) {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    const fetchHealth = () => {
      getHealth()
        .then((res) => setHealth(res.data))
        .catch(() => setHealth(null));
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'landing', label: 'Overview', icon: Sparkles },
    { id: 'playground', label: 'Playground', icon: Terminal },
    { id: 'comparison', label: 'Compare Models', icon: Layers },
    { id: 'database', label: 'Database Explorer', icon: Database },
    { id: 'finetuning', label: 'Fine-Tuning Lab', icon: Sliders },
    { id: 'evaluation', label: 'Evaluation', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-[#090d16]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
        {/* Brand */}
        <div
          onClick={() => setActiveTab('landing')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Database className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white group-hover:text-cyan-400 transition-colors">
                QueryMind
              </span>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                LLM Research
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono hidden sm:block">Text-to-SQL Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span className="hidden md:inline">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System & GPU Status Pill */}
        <div className="hidden lg:flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <span
              className={`w-2 h-2 rounded-full ${
                health?.status === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
              }`}
            />
            <span className="font-mono">
              {health?.gpu?.cuda_available
                ? `${health.gpu.device_name.replace('NVIDIA GeForce ', '')}`
                : 'RTX 4060'}
            </span>
            {health?.gpu?.cuda_available && (
              <span className="text-slate-500 font-mono">
                {Math.round(health.gpu.free_mb / 1024)}GB Free
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

