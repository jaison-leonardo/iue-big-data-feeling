import React, { useState } from 'react';
import Stats from './components/Stats';
import SentimentsTable from './components/SentimentsTable';
import PredictForm from './components/PredictForm';
import PowerBIEmbed from './components/PowerBIEmbed';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleNewPrediction = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="text-center">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-2">
            SentimentStream
          </h1>
          <p className="text-slate-500 text-lg">
            Análisis de sentimientos en tiempo real propulsado por Machine Learning
          </p>
        </header>

        {/* Top Section: Stats & Predict */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Stats refreshTrigger={refreshTrigger} />
          </div>
          <div className="lg:col-span-1">
            <PredictForm onPredictSuccess={handleNewPrediction} />
          </div>
        </div>

        {/* Middle Section: Table */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-xl font-bold text-slate-800 mb-4">Últimos Análisis</h2>
          <SentimentsTable refreshTrigger={refreshTrigger} />
        </div>

        {/* Bottom Section: Power BI */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-xl font-bold text-slate-800 mb-4">Dashboard de Inteligencia de Negocios</h2>
          <PowerBIEmbed />
        </div>
        
      </div>
    </div>
  );
}

export default App;
