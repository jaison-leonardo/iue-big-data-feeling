import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const API = import.meta.env.VITE_API_URL;

const Stats = ({ refreshTrigger }) => {
  const [stats, setStats] = useState({ positivo: 0, negativo: 0, neutral: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API}/stats`);
      if (!response.ok) throw new Error('Error al obtener estadísticas');
      const data = await response.json();
      setStats({
        positivo: data.positivo || 0,
        negativo: data.negativo || 0,
        neutral: data.neutral || 0,
      });
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  if (loading) return <div className="animate-pulse flex space-x-4 h-32 glass rounded-2xl p-6">Cargando estadísticas...</div>;
  if (error) return <div className="text-red-500 glass rounded-2xl p-6 bg-red-50">Error: {error}</div>;

  const total = stats.positivo + stats.negativo + stats.neutral;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Tarjeta Positivo */}
      <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center border-l-4 border-emerald-500 transition-transform hover:scale-105">
        <div className="bg-emerald-100 p-3 rounded-full mb-3">
          <TrendingUp className="w-8 h-8 text-emerald-600" />
        </div>
        <span className="text-3xl font-bold text-slate-800">{stats.positivo}</span>
        <span className="text-sm font-medium text-emerald-600 uppercase tracking-wider mt-1">Positivos</span>
      </div>

      {/* Tarjeta Neutral */}
      <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center border-l-4 border-slate-400 transition-transform hover:scale-105">
        <div className="bg-slate-100 p-3 rounded-full mb-3">
          <Minus className="w-8 h-8 text-slate-500" />
        </div>
        <span className="text-3xl font-bold text-slate-800">{stats.neutral}</span>
        <span className="text-sm font-medium text-slate-500 uppercase tracking-wider mt-1">Neutrales</span>
      </div>

      {/* Tarjeta Negativo */}
      <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center border-l-4 border-rose-500 transition-transform hover:scale-105">
        <div className="bg-rose-100 p-3 rounded-full mb-3">
          <TrendingDown className="w-8 h-8 text-rose-600" />
        </div>
        <span className="text-3xl font-bold text-slate-800">{stats.negativo}</span>
        <span className="text-sm font-medium text-rose-600 uppercase tracking-wider mt-1">Negativos</span>
      </div>
    </div>
  );
};

export default Stats;
