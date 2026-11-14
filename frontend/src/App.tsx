import { useState, useEffect } from 'react';
import { TopBar } from './components/TopBar';
import { AnalyzeTab } from './components/AnalyzeTab';
import { ConversationsTab } from './components/ConversationsTab';
import { InsightsTab } from './components/InsightsTab';
import { checkHealth } from './api/client';
import { Info, Check, AlertTriangle } from 'lucide-react';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export function App() {
  const [activeTab, setActiveTab] = useState<'analyze' | 'conversations' | 'insights'>('analyze');
  const [isApiOnline, setIsApiOnline] = useState<boolean>(true);
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Health Polling (every 5 seconds)
  useEffect(() => {
    const verifyHealth = async () => {
      const online = await checkHealth();
      setIsApiOnline(online);
    };

    verifyHealth();
    const interval = setInterval(verifyHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  };

  return (
    <div className="min-h-screen bg-page flex flex-col selection:bg-brand/30 selection:text-white">
      
      {/* Sticky TopBar */}
      <TopBar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isApiOnline={isApiOnline}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {activeTab === 'analyze' && <AnalyzeTab onNotify={showToast} />}
        {activeTab === 'conversations' && <ConversationsTab onNotify={showToast} />}
        {activeTab === 'insights' && <InsightsTab />}
      </main>

      {/* Footer & Ethical Use Notice */}
      <footer className="border-t border-cardBorder/80 py-6 text-center text-xs text-muted font-mono bg-[#0c0c0e]">
        <div className="max-w-[1000px] mx-auto px-4 space-y-2">
          <p className="flex items-center justify-center gap-1.5 text-neutral-400">
            <Info className="w-3.5 h-3.5 text-brand" />
            <span>Tone Checker (VibeCheck) — Multi-Label Toxicity & Tone Intelligence</span>
          </p>
          <p className="text-[11px] text-muted/70 max-w-2xl mx-auto leading-relaxed">
            Ethical-use note: Model evaluations are probabilistic advisory metrics. This system is designed as an assistive writing tool to foster empathetic, constructive dialogue—not as an automated censor or punitive moderator.
          </p>
        </div>
      </footer>

      {/* Floating Notification Toasts */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center gap-2.5 px-4 py-2.5 rounded-lg border text-xs font-mono shadow-2xl transition-all ${
              t.type === 'success'
                ? 'bg-[#12241b] border-safe/40 text-safe'
                : t.type === 'error'
                ? 'bg-[#291414] border-toxic/40 text-toxic'
                : 'bg-[#18181c] border-cardBorder text-neutral-200'
            }`}
          >
            {t.type === 'success' && <Check className="w-4 h-4 text-safe" />}
            {t.type === 'error' && <AlertTriangle className="w-4 h-4 text-toxic" />}
            {t.type === 'info' && <Info className="w-4 h-4 text-brand" />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>

    </div>
  );
}

export default App;
