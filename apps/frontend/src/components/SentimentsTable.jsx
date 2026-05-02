import React, { useState, useEffect } from 'react';

const API = import.meta.env.VITE_API_URL;

const SentimentsTable = ({ refreshTrigger }) => {
  const [sentiments, setSentiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSentiments = async () => {
    try {
      const response = await fetch(`${API}/sentiments?limit=20`);
      if (!response.ok) throw new Error('Error al obtener la tabla de sentimientos');
      const data = await response.json();
      setSentiments(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSentiments();
    const interval = setInterval(fetchSentiments, 5000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  if (loading) return <div className="p-4 text-slate-500">Cargando registros...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;
  if (sentiments.length === 0) return <div className="p-4 text-slate-500">No hay datos disponibles.</div>;

  const getBadgeColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positivo': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'negativo': return 'bg-rose-100 text-rose-800 border-rose-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm text-slate-600">
        <thead className="bg-slate-50 text-slate-700 uppercase font-semibold border-b border-slate-200">
          <tr>
            <th className="px-6 py-4">Texto Analizado</th>
            <th className="px-6 py-4">Sentimiento</th>
            <th className="px-6 py-4">Confianza</th>
            <th className="px-6 py-4">Fecha</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {sentiments.map((item, idx) => (
            <tr key={idx} className="hover:bg-slate-50 transition-colors">
              <td className="px-6 py-4 font-medium text-slate-900 truncate max-w-md" title={item.texto}>
                {item.texto}
              </td>
              <td className="px-6 py-4">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getBadgeColor(item.sentimiento)}`}>
                  {item.sentimiento}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <div className="w-full bg-slate-200 rounded-full h-2.5 max-w-[100px]">
                    <div 
                      className="bg-indigo-600 h-2.5 rounded-full" 
                      style={{ width: `${(item.confianza * 100).toFixed(0)}%` }}
                    ></div>
                  </div>
                  <span className="text-xs">{(item.confianza * 100).toFixed(1)}%</span>
                </div>
              </td>
              <td className="px-6 py-4 text-xs whitespace-nowrap">
                {new Date(item.timestamp).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SentimentsTable;
