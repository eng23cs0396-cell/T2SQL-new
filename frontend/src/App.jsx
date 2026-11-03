import React, { useState } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import PlaygroundPage from './pages/PlaygroundPage';
import ComparisonPage from './pages/ComparisonPage';
import FineTuningLabPage from './pages/FineTuningLabPage';
import EvaluationDashboardPage from './pages/EvaluationDashboardPage';
import DatabaseExplorerPage from './pages/DatabaseExplorerPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('playground');

  return (
    <div className="min-h-screen bg-[#070b13] text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Professional Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main View Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {activeTab === 'landing' && (
          <LandingPage
            onStartQuerying={() => setActiveTab('playground')}
            onExploreModels={() => setActiveTab('comparison')}
          />
        )}
        {activeTab === 'playground' && <PlaygroundPage />}
        {activeTab === 'comparison' && <ComparisonPage />}
        {activeTab === 'database' && <DatabaseExplorerPage />}
        {activeTab === 'finetuning' && <FineTuningLabPage />}
        {activeTab === 'evaluation' && <EvaluationDashboardPage />}
      </main>
    </div>
  );
}
