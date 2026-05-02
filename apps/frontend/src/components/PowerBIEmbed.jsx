import React from 'react';

const PowerBIEmbed = () => {
  const powerBiUrl = import.meta.env.VITE_POWERBI_URL;

  if (!powerBiUrl || powerBiUrl.includes('YOUR_REPORT_ID')) {
    return (
      <div className="w-full h-[500px] bg-slate-100 rounded-xl border-2 border-dashed border-slate-300 flex flex-col items-center justify-center text-slate-500">
        <p className="font-medium mb-2">Dashboard de Power BI no configurado</p>
        <p className="text-sm">Configura VITE_POWERBI_URL en el archivo .env</p>
      </div>
    );
  }

  return (
    <div className="w-full h-[500px] rounded-xl overflow-hidden border border-slate-200 bg-white">
      <iframe
        title="Sentiment Power BI Dashboard"
        src={powerBiUrl}
        width="100%"
        height="100%"
        frameBorder="0"
        allowFullScreen={true}
        className="w-full h-full"
      ></iframe>
    </div>
  );
};

export default PowerBIEmbed;
