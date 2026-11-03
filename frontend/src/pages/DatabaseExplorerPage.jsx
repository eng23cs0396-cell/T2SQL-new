import React, { useState, useEffect } from 'react';
import {
  Database,
  Upload,
  Table as TableIcon,
  Key,
  Link as LinkIcon,
  Eye,
  RefreshCw,
  HardDrive,
  Info
} from 'lucide-react';
import {
  listDatabases,
  uploadDatabase,
  getDatabaseSchema,
  getTablePreview
} from '../services/api';

export default function DatabaseExplorerPage() {
  const [databases, setDatabases] = useState([]);
  const [selectedDbId, setSelectedDbId] = useState('');
  const [schemaData, setSchemaData] = useState(null);
  const [selectedTable, setSelectedTable] = useState('');
  const [tablePreview, setTablePreview] = useState(null);
  const [previewLimit, setPreviewLimit] = useState(10);
  const [uploading, setUploading] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchDatabases();
  }, []);

  const fetchDatabases = async () => {
    try {
      const res = await listDatabases();
      setDatabases(res.data);
      if (res.data.length > 0 && !selectedDbId) {
        setSelectedDbId(res.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching databases:', err);
    }
  };

  useEffect(() => {
    if (!selectedDbId) return;
    const fetchSchema = async () => {
      try {
        const res = await getDatabaseSchema(selectedDbId);
        setSchemaData(res.data);
        const tables = Object.keys(res.data.tables || {});
        if (tables.length > 0) {
          setSelectedTable(tables[0]);
        } else {
          setSelectedTable('');
          setTablePreview(null);
        }
      } catch (err) {
        console.error('Error fetching schema:', err);
      }
    };
    fetchSchema();
  }, [selectedDbId]);

  useEffect(() => {
    if (!selectedDbId || !selectedTable) return;
    const fetchPreview = async () => {
      setLoadingPreview(true);
      try {
        const res = await getTablePreview(selectedDbId, selectedTable, previewLimit);
        setTablePreview(res.data);
      } catch (err) {
        console.error('Error fetching table preview:', err);
      } finally {
        setLoadingPreview(false);
      }
    };
    fetchPreview();
  }, [selectedDbId, selectedTable, previewLimit]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setErrorMsg('');
    try {
      const res = await uploadDatabase(file);
      await fetchDatabases();
      setSelectedDbId(res.data.database.id);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to upload database file.');
    } finally {
      setUploading(false);
    }
  };

  const activeDbInfo = databases.find((d) => d.id === selectedDbId);
  const activeTableData = schemaData?.tables?.[selectedTable];

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-3">
            <Database className="w-7 h-7 text-cyan-400" />
            Database & Schema Explorer
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Introspect relational tables, data types, primary/foreign keys, and preview records across active SQLite databases.
          </p>
        </div>

        <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-lg shadow-cyan-600/20 transition-all self-start sm:self-auto">
          <Upload className="w-4 h-4" />
          <span>{uploading ? 'Uploading...' : 'Upload SQLite File'}</span>
          <input
            type="file"
            accept=".db,.sqlite,.sqlite3"
            onChange={handleUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {errorMsg && (
        <div className="p-3.5 rounded-xl border border-rose-900/60 bg-rose-950/20 text-xs text-rose-300 font-mono">
          {errorMsg}
        </div>
      )}

      {/* Database Switcher Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {databases.map((db) => {
          const isSelected = db.id === selectedDbId;
          return (
            <button
              key={db.id}
              onClick={() => setSelectedDbId(db.id)}
              className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-cyan-950/40 border-cyan-500/80 shadow-lg text-white'
                  : 'bg-[#0d1322] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between w-full mb-2">
                <Database className={`w-4 h-4 ${isSelected ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                  {db.table_count} tables
                </span>
              </div>
              <div>
                <span className="font-bold text-xs truncate block text-slate-200">{db.name}</span>
                <span className="text-[10px] text-slate-500 font-mono mt-0.5 block">
                  {Math.round(db.size_bytes / 1024)} KB
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Schema & Data Preview Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Tables List & Relationships */}
        <div className="lg:col-span-4 space-y-5">
          {/* Table Selector */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-3">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
              Tables in Database
            </span>
            <div className="space-y-1.5">
              {Object.keys(schemaData?.tables || {}).map((tableName) => {
                const isSelected = tableName === selectedTable;
                const colCount = schemaData.tables[tableName].columns.length;
                const rowCount = schemaData.tables[tableName].row_count;
                return (
                  <button
                    key={tableName}
                    onClick={() => setSelectedTable(tableName)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-mono text-left transition-all ${
                      isSelected
                        ? 'bg-slate-800 text-cyan-300 border border-slate-700 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    }`}
                  >
                    <span className="font-semibold">{tableName}</span>
                    <span className="text-[10px] text-slate-500">
                      {rowCount} rows &bull; {colCount} cols
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Relationships Card */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-3">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <LinkIcon className="w-3.5 h-3.5 text-indigo-400" />
              <span>Foreign Key Relationships</span>
            </span>

            {(!schemaData?.relationships || schemaData.relationships.length === 0) ? (
              <p className="text-xs text-slate-500 italic">No explicit foreign keys declared in database.</p>
            ) : (
              <div className="space-y-2">
                {schemaData.relationships.map((rel, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg border border-slate-800/80 bg-slate-900/60 text-xs font-mono text-slate-300 space-y-0.5"
                  >
                    <div className="text-cyan-400">
                      {rel.from_table}.{rel.from_col}
                    </div>
                    <div className="text-slate-500 text-[10px]">references</div>
                    <div className="text-purple-400">
                      {rel.to_table}.{rel.to_col}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Active Table Schema & Live Data Grid */}
        <div className="lg:col-span-8 space-y-6">
          {/* Active Table Schema Card */}
          {activeTableData && (
            <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <TableIcon className="w-4 h-4 text-cyan-400" />
                  <h3 className="font-bold text-white text-base font-mono">{selectedTable}</h3>
                </div>
                <span className="text-xs font-mono text-slate-400">
                  {activeTableData.columns.length} Columns
                </span>
              </div>

              {/* Columns Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                {activeTableData.columns.map((col) => (
                  <div
                    key={col.name}
                    className="p-2.5 rounded-lg border border-slate-800/70 bg-slate-900/60 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-1.5">
                      {col.is_primary_key && <Key className="w-3.5 h-3.5 text-amber-400" />}
                      <span className="font-semibold text-slate-200">{col.name}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] text-slate-400">{col.type}</span>
                      {col.is_primary_key && (
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          PK
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Live Data Records Preview */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-[#0d1322] shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-emerald-400" />
                <h3 className="font-bold text-white text-base">Sample Records Preview</h3>
              </div>

              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-slate-500">Limit:</span>
                {[10, 25, 50].map((l) => (
                  <button
                    key={l}
                    onClick={() => setPreviewLimit(l)}
                    className={`px-2 py-0.5 rounded text-xs ${
                      previewLimit === l
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>

            {loadingPreview ? (
              <div className="py-12 flex flex-col items-center justify-center">
                <RefreshCw className="w-6 h-6 animate-spin text-cyan-400 mb-2" />
                <span className="text-xs text-slate-500 font-mono">Loading records...</span>
              </div>
            ) : !tablePreview || tablePreview.rows?.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500 font-mono">
                Table currently contains 0 records.
              </div>
            ) : (
              <div className="overflow-x-auto max-h-[360px]">
                <table className="w-full text-left text-xs font-mono border-collapse">
                  <thead>
                    <tr className="bg-slate-900 border-b border-slate-800 text-slate-300 sticky top-0">
                      <th className="py-2 px-3 text-slate-600 text-center w-8">#</th>
                      {tablePreview.columns.map((c) => (
                        <th key={c} className="py-2 px-3 font-semibold text-cyan-300 whitespace-nowrap">
                          {c}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {tablePreview.rows.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-2 px-3 text-slate-600 text-center">{rIdx + 1}</td>
                        {tablePreview.columns.map((colName) => (
                          <td key={colName} className="py-2 px-3 text-slate-300 whitespace-nowrap">
                            {row[colName] === null ? (
                              <span className="text-slate-600 italic">NULL</span>
                            ) : typeof row[colName] === 'number' ? (
                              <span className="text-amber-300">{row[colName]}</span>
                            ) : (
                              String(row[colName])
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

