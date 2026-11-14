import React from 'react';
import { Shield, Sparkles, MessageSquare, BarChart3 } from 'lucide-react';

interface TopBarProps {
  activeTab: 'analyze' | 'conversations' | 'insights';
  onTabChange: (tab: 'analyze' | 'conversations' | 'insights') => void;
  isApiOnline: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  activeTab,
  onTabChange,
  isApiOnline
}) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-cardBorder bg-page/95 backdrop-blur-md">
      <div className="max-w-[1000px] mx-auto px-4 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => onTabChange('analyze')}>
          <div className="w-9 h-9 rounded-xl bg-brand flex items-center justify-center text-white shadow-lg shadow-brand/20">
            <Shield className="w-5 h-5 fill-white/20 stroke-white stroke-[2.2]" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg tracking-tight text-white font-sans">
                Vibe<span className="text-brand">Check</span>
              </span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-brand/10 text-brand border border-brand/20">
                v1.0
              </span>
            </div>
          </div>
        </div>

        {/* Center: Segmented Tab Control */}
        <nav className="flex items-center p-1 rounded-xl bg-card border border-cardBorder">
          <button
            onClick={() => onTabChange('analyze')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeTab === 'analyze'
                ? 'bg-brand text-white font-semibold shadow-sm'
                : 'text-muted hover:text-white hover:bg-white/5'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Analyze</span>
          </button>

          <button
            onClick={() => onTabChange('conversations')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeTab === 'conversations'
                ? 'bg-brand text-white font-semibold shadow-sm'
                : 'text-muted hover:text-white hover:bg-white/5'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Conversations</span>
          </button>

          <button
            onClick={() => onTabChange('insights')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeTab === 'insights'
                ? 'bg-brand text-white font-semibold shadow-sm'
                : 'text-muted hover:text-white hover:bg-white/5'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Insights</span>
          </button>
        </nav>

        {/* Right: API Status Pill */}
        <div className="flex items-center">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono border ${
            isApiOnline
              ? 'bg-safe-bg border-safe-border text-safe'
              : 'bg-toxic-bg border-toxic-border text-toxic'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              isApiOnline ? 'bg-safe animate-pulse' : 'bg-toxic'
            }`} />
            <span>API: {isApiOnline ? 'online' : 'offline'}</span>
          </div>
        </div>

      </div>
    </header>
  );
};
