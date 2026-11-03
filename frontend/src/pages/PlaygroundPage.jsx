import React, { useState, useEffect } from 'react';
import {
  Database,
  Play,
  Upload,
  RefreshCw,
  Sliders,
  Cpu,
  Zap,
  ChevronRight,
  ChevronDown,
  Info,
  Key,
  Link as LinkIcon,
  HelpCircle,
  Clock,
  Sparkles
} from 'lucide-react';
import {
  listDatabases,
  uploadDatabase,
  getDatabaseSchema,
  generateSQL,
  executeSQL,
  listAdapters,
} from '../services/api';
import SQLEditor from '../components/SQLEditor';
import DataTable from '../components/DataTable';

export default function PlaygroundPage() {
  // Databases & Schema State
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState('');
  const [schemaData, setSchemaData] = useState(null);
  const [expandedTables, setExpandedTables] = useState({});
  const [uploading, setUploading] = useState(false);

  // Model & Technique Selection State
  const [selectedModel, setSelectedModel] = useState('nemotron'); // 'nemotron' | 'qwen'
  const [selectedTechnique, setSelectedTechnique] = useState('zero_shot'); // 'zero_shot' | 'few_shot' | 'lora'
  const [numFewShot, setNumFewShot] = useState(3);
  const [adapters, setAdapters] = useState([]);
  const [selectedAdapter, setSelectedAdapter] = useState('');

  // Input & Generation State
  const [question, setQuestion] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState(null);
  const [editableSql, setEditableSql] = useState('');

  // Execution State
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  // Load databases and adapters on mount
  useEffect(() => {
    fetchDatabases();
    fetchAdapters();
  }, []);

  const fetchDatabases = async () => {
    try {
      const res = await listDatabases();
      setDatabases(res.data);
      if (res.data.length > 0 && !selectedDb) {
        setSelectedDb(res.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching databases:', err);
    }
  };

  const fetchAdapters = async () => {
    try {
      const res = await listAdapters();
      setAdapters(res.data);
      if (res.data.length > 0 && !selectedAdapter) {
        setSelectedAdapter(res.data[0].name);
      }
    } catch (err) {
      console.error('Error fetching adapters:', err);
    }
  };

  // Fetch schema when database selection changes
  useEffect(() => {
    if (!selectedDb) return;
    const fetchSchema = async () => {
      try {
        const res = await getDatabaseSchema(selectedDb);
        setSchemaData(res.data);
        // Expand first table by default
        if (res.data.tables) {
          const firstTable = Object.keys(res.data.tables)[0];
          setExpandedTables({ [firstTable]: true });
        }
      } catch (err) {
        console.error('Error fetching schema:', err);
      }
    };
    fetchSchema();
  }, [selectedDb]);

  // Adjust default technique when model changes
  useEffect(() => {
    if (selectedModel === 'nemotron') {
      setSelectedTechnique('zero_shot');
    } else {
      setSelectedTechnique('few_shot');
    }
  }, [selectedModel]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setErrorMessage('');
    try {
      const res = await uploadDatabase(file);
      await fetchDatabases();
      setSelectedDb(res.data.database.id);
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Failed to upload database file.');
    } finally {
      setUploading(false);
    }
  };

  const toggleTableExpand = (table) => {
    setExpandedTables((prev) => ({ ...prev, [table]: !prev[table] }));
  };

  const handleGenerate = async () => {
    if (!question.trim()) {
      setErrorMessage('Please enter a natural language question.');
      return;
    }
    if (!selectedDb) {
      setErrorMessage('Please select a database.');
      return;
    }

    setGenerating(true);
    setErrorMessage('');
    setGenerationResult(null);
    setExecutionResult(null);

    try {
      const payload = {
        database_id: selectedDb,
        question: question.trim(),
        model: selectedModel,
        technique: selectedTechnique,
        num_few_shot_examples: numFewShot,
        adapter_name: selectedTechnique === 'lora' ? selectedAdapter : null,
      };

      const res = await generateSQL(payload);
      setGenerationResult(res.data);
      setEditableSql(res.data.generated_sql || '');

      // If valid, auto-populate execution preview
      if (res.data.execution) {
        setExecutionResult(res.data.execution);
      }
      if (res.data.error) {
        setErrorMessage(res.data.error);
      }
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || err.message || 'Generation failed.');
    } finally {
      setGenerating(false);
    }
  };

  const handleManualExecute = async () => {
    if (!editableSql.trim()) return;
    setExecuting(true);
    setErrorMessage('');
    try {
      const res = await executeSQL({
        database_id: selectedDb,
        sql: editableSql.trim(),
      });
      setExecutionResult(res.data);
      if (!res.data.success && res.data.error) {
        setErrorMessage(res.data.error);
      }
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Query execution failed.');
    } finally {
      setExecuting(false);
    }
  };

  // Example suggestions based on current database
  const getSuggestions = () => {
    if (selectedDb.includes('university')) {
      return [
        'Find the top 3 oldest students with their ages.',
        'What is the highest salary among instructors?',
        'List department names and the count of students in each.',
        'Find instructors who belong to the Computer Science department.'
      ];
    } else if (selectedDb.includes('ecommerce')) {
      return [
        'Find all delivered orders and their total amounts.',
        'List products that have unit price greater than 100.',
        'Find the total amount spent by customer Michael Scott.',
        'What is the average product unit price in each category?'
      ];
    } else if (selectedDb.includes('course_teach')) {
      return [
        'How many teachers are there in total?',
        'List the names of teachers in ascending order of age.',
        'What are the distinct hometowns of teachers?'
      ];
    } else if (selectedDb.includes('department_management')) {
      return [
        'How many department heads are older than 50?',
        'List the creation year and name of each department.',
        'What is the maximum budget among all departments?'
      ];
    }
    return [
      'Show all records from the primary table.',
      'Count the total number of entries.',
      'Find the entry with the maximum ID.'
    ];
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pb-12">
      {/* ============================================================ */}
      {/* LEFT SIDEBAR: DATABASE & SCHEMA BROWSER + MODEL SELECTOR */}
      {/* ============================================================ */}
      <aside className="lg:col-span-4 space-y-5">
        {/* Database Selection Card */}
        <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322] shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>Target Database</span>
            </label>

            <label className="cursor-pointer text-xs font-medium text-cyan-400 hover:text-cyan-300 flex items-center gap-1 bg-cyan-500/10 hover:bg-cyan-500/20 px-2.5 py-1 rounded-md border border-cyan-500/20 transition-all">
              <Upload className="w-3.5 h-3.5" />
              <span>{uploading ? 'Uploading...' : 'Upload DB'}</span>
              <input
                type="file"
                accept=".db,.sqlite,.sqlite3"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>

          <select
            value={selectedDb}
            onChange={(e) => setSelectedDb(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
          >
            {databases.map((db) => (
              <option key={db.id} value={db.id}>
                {db.name} ({db.table_count} tables, {Math.round(db.size_bytes / 1024)} KB)
              </option>
            ))}
          </select>
        </div>

        {/* Model Selection Card */}
        <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322] shadow-lg space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 mb-2.5">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>Inference Model</span>
            </label>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setSelectedModel('nemotron')}
                className={`flex flex-col items-start p-3 rounded-lg border text-left transition-all ${
                  selectedModel === 'nemotron'
                    ? 'bg-indigo-950/40 border-indigo-500/60 shadow-md text-white'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-1.5 font-bold text-xs">
                  <Zap className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Nemotron 3.5</span>
                </div>
                <span className="text-[11px] text-slate-400 mt-1">NVIDIA NIM API</span>
              </button>

              <button
                onClick={() => setSelectedModel('qwen')}
                className={`flex flex-col items-start p-3 rounded-lg border text-left transition-all ${
                  selectedModel === 'qwen'
                    ? 'bg-indigo-950/40 border-indigo-500/60 shadow-md text-white'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-1.5 font-bold text-xs">
                  <Cpu className="w-3.5 h-3.5 text-purple-400" />
                  <span>Qwen2.5-Coder</span>
                </div>
                <span className="text-[11px] text-slate-400 mt-1">Local GPU (8GB)</span>
              </button>
            </div>
          </div>

          {/* Model-Specific Sub-Technique Settings */}
          {selectedModel === 'nemotron' ? (
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-400 space-y-1">
              <div className="flex items-center justify-between text-slate-300 font-semibold">
                <span>Model ID</span>
                <span className="font-mono text-[11px] text-cyan-400">nemotron-3.5-lightning-30b-a3b</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Temperature set to 0.0 with internal thinking disabled for instant SQL synthesis.
              </p>
            </div>
          ) : (
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-3">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
                Local Qwen Technique
              </label>

              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedTechnique('few_shot')}
                  className={`flex-1 py-1.5 px-2 rounded-md text-xs font-medium border text-center transition-all ${
                    selectedTechnique === 'few_shot'
                      ? 'bg-purple-600 text-white border-purple-500'
                      : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
                  }`}
                >
                  Few-Shot Prompting
                </button>

                <button
                  onClick={() => setSelectedTechnique('lora')}
                  className={`flex-1 py-1.5 px-2 rounded-md text-xs font-medium border text-center transition-all ${
                    selectedTechnique === 'lora'
                      ? 'bg-purple-600 text-white border-purple-500'
                      : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
                  }`}
                >
                  LoRA Fine-Tuned
                </button>
              </div>

              {selectedTechnique === 'few_shot' && (
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-slate-400">Demonstration Count</span>
                  <div className="flex gap-1">
                    {[3, 4, 5].map((n) => (
                      <button
                        key={n}
                        onClick={() => setNumFewShot(n)}
                        className={`w-7 h-6 rounded text-xs font-mono font-bold ${
                          numFewShot === n
                            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                            : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {selectedTechnique === 'lora' && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-xs text-slate-400">Adapter Checkpoint</span>
                  {adapters.length === 0 ? (
                    <div className="text-[11px] text-amber-400 bg-amber-500/10 p-2 rounded border border-amber-500/20">
                      No trained adapter found yet. Train one in the Fine-Tuning Lab or use Few-Shot.
                    </div>
                  ) : (
                    <select
                      value={selectedAdapter}
                      onChange={(e) => setSelectedAdapter(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono"
                    >
                      {adapters.map((ad) => (
                        <option key={ad.name} value={ad.name}>
                          {ad.name} (r={ad.rank}, {ad.size_mb} MB)
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Schema Tree Browser */}
        <div className="p-4 rounded-xl border border-slate-800 bg-[#0d1322] shadow-lg max-h-[460px] flex flex-col">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>Extracted Schema</span>
            </span>
            <span className="text-xs font-mono text-slate-500">
              {schemaData?.tables ? Object.keys(schemaData.tables).length : 0} Tables
            </span>
          </div>

          <div className="overflow-y-auto space-y-2 pr-1">
            {!schemaData ? (
              <p className="text-xs text-slate-500 italic">Loading schema metadata...</p>
            ) : (
              Object.entries(schemaData.tables || {}).map(([tableName, tData]) => {
                const isExpanded = !!expandedTables[tableName];
                return (
                  <div key={tableName} className="rounded-lg border border-slate-800 bg-slate-900/60 overflow-hidden">
                    <button
                      onClick={() => toggleTableExpand(tableName)}
                      className="w-full flex items-center justify-between p-2.5 text-left text-xs font-mono text-slate-200 hover:bg-slate-800/60 transition-colors"
                    >
                      <span className="font-semibold text-cyan-300">{tableName}</span>
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <span className="text-[10px]">{tData.columns.length} cols</span>
                        {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="px-3 pb-2 pt-1 border-t border-slate-800/60 space-y-1.5 text-xs font-mono">
                        {tData.columns.map((col) => (
                          <div key={col.name} className="flex items-center justify-between py-0.5 text-slate-300">
                            <span className="text-slate-200 flex items-center gap-1">
                              {col.is_primary_key && <Key className="w-3 h-3 text-amber-400" />}
                              {col.name}
                            </span>
                            <span className="text-[10px] text-slate-500">{col.type}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </aside>

      {/* ============================================================ */}
      {/* MAIN PLAYGROUND WORKSPACE */}
      {/* ============================================================ */}
      <main className="lg:col-span-8 space-y-6">
        {/* User Question Area */}
        <div className="p-5 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Natural Language Question</span>
            </label>
            <span className="text-xs text-slate-500 font-mono">{question.length} chars</span>
          </div>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Find the top 3 oldest students based on their age."
            rows={3}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 resize-none"
          />

          {/* Quick Suggestions Chips */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
              Suggested Questions
            </span>
            <div className="flex flex-wrap gap-2">
              {getSuggestions().map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => setQuestion(sug)}
                  className="text-xs font-medium px-2.5 py-1 rounded-md bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/60 transition-all text-left"
                >
                  &ldquo;{sug}&rdquo;
                </button>
              ))}
            </div>
          </div>

          {/* Action Button & Status Bar */}
          <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
            <div className="text-xs text-slate-500 font-mono">
              Workflow: Dynamic Schema &bull; LangChain Prompt &bull; {selectedModel.toUpperCase()} &bull; SQLGlot AST
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating || !question.trim()}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold shadow-lg shadow-indigo-500/20 hover:from-cyan-400 hover:to-indigo-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  <span>Generating SQL...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Generate SQL</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Global Error Banner */}
        {errorMessage && (
          <div className="p-3.5 rounded-xl border border-rose-900/60 bg-rose-950/20 text-xs text-rose-300 font-mono">
            <span className="font-bold text-rose-200">Alert:</span> {errorMessage}
          </div>
        )}

        {/* Generation Metadata Bar (If generated) */}
        {generationResult && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg border border-slate-800 bg-[#0d1322]">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Model Used</span>
              <span className="text-xs font-semibold text-slate-200 truncate block">
                {generationResult.model_used || selectedModel}
              </span>
            </div>

            <div className="p-3 rounded-lg border border-slate-800 bg-[#0d1322]">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Technique</span>
              <span className="text-xs font-semibold text-cyan-400 truncate block">
                {generationResult.technique_used || selectedTechnique}
              </span>
            </div>

            <div className="p-3 rounded-lg border border-slate-800 bg-[#0d1322]">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Latency</span>
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1 font-mono">
                <Clock className="w-3.5 h-3.5" />
                {generationResult.generation_time_ms} ms
              </span>
            </div>

            <div className="p-3 rounded-lg border border-slate-800 bg-[#0d1322]">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Security Check</span>
              <span
                className={`text-xs font-semibold font-mono ${
                  generationResult.validation?.valid ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {generationResult.validation?.valid ? 'PASS (Read-Only)' : 'FAIL'}
              </span>
            </div>
          </div>
        )}

        {/* Generated SQL Editor */}
        <div className="space-y-3">
          <SQLEditor
            sql={editableSql}
            validation={generationResult?.validation}
            readOnly={false}
            onChange={(val) => setEditableSql(val)}
          />

          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 font-mono">
              You can edit the SQL query directly before running execution.
            </span>

            <button
              onClick={handleManualExecute}
              disabled={executing || !editableSql.trim()}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
            >
              {executing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Running Query...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute Query</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Query Results Table */}
        <DataTable executionResult={executionResult} loading={executing} />
      </main>
    </div>
  );
}

