import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

const API = import.meta.env.VITE_API_URL;

const PredictForm = ({ onPredictSuccess }) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: text }),
      });

      if (!response.ok) {
        throw new Error('Error al procesar la predicción');
      }

      const data = await response.json();
      setResult(data);
      setText('');
      if (onPredictSuccess) onPredictSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass rounded-2xl p-6 h-full flex flex-col">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Analizar Texto</h2>
      
      <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4">
        <textarea
          className="w-full flex-1 p-4 bg-white/50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none transition-all placeholder:text-slate-400"
          placeholder="Escribe un comentario o reseña aquí..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={loading}
        />
        
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-colors flex justify-center items-center gap-2"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <span>Procesar</span>
              <Send className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-indigo-50 border border-indigo-100 rounded-xl animate-fade-in">
          <p className="text-sm text-slate-600 mb-1">Último resultado:</p>
          <div className="flex items-center justify-between">
            <span className="font-bold text-indigo-900 uppercase tracking-wide">
              {result.sentimiento}
            </span>
            <span className="text-sm font-medium text-indigo-600">
              {(result.confianza * 100).toFixed(1)}% confianza
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictForm;
