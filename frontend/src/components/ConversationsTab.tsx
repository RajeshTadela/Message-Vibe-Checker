import React, { useState, useEffect } from 'react';
import {
  Upload,
  MessageSquare,
  TrendingUp,
  RefreshCw,
  History,
  CheckCircle2,
  AlertTriangle,
  Flame
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { ConversationDetail, ConversationSummary } from '../types';
import {
  createConversation,
  fetchConversations,
  fetchConversation
} from '../api/client';

interface ConversationsTabProps {
  onNotify?: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

const DEFAULT_CHAT_SAMPLE = `Alice: Hey team, please review the latest API spec for payment webhooks.
Bob: Stop asking basic questions and read the documentation first.
Charlie: Seriously Bob, you are an absolute idiot and a complete moron.
Alice: Let's keep our communication polite and constructive, please.
Bob: Whatever. Don't ping me about this again.`;

export const ConversationsTab: React.FC<ConversationsTabProps> = ({ onNotify }) => {
  const [chatInput, setChatInput] = useState<string>(DEFAULT_CHAT_SAMPLE);
  const [chatTitle, setChatTitle] = useState<string>('Sprint Retrospective #42');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetail | null>(null);
  const [historyList, setHistoryList] = useState<ConversationSummary[]>([]);

  // Load conversation history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await fetchConversations();
      setHistoryList(data);
    } catch (err) {
      console.error('Failed to load conversation history', err);
    }
  };

  const handleProcessChat = async () => {
    if (!chatInput.trim()) {
      if (onNotify) onNotify('Please enter or paste chat messages.', 'error');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await createConversation(chatInput.trim(), chatTitle.trim() || undefined);
      setCurrentConversation(result);
      if (onNotify) onNotify(`Parsed ${result.message_count} messages successfully!`, 'success');
      loadHistory();
    } catch (err: any) {
      if (onNotify) onNotify(err.message || 'Failed to process chat', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSelectHistory = async (id: number) => {
    setIsProcessing(true);
    try {
      const detail = await fetchConversation(id);
      setCurrentConversation(detail);
      setChatInput(detail.raw_text);
      setChatTitle(detail.title);
    } catch (err: any) {
      if (onNotify) onNotify(err.message || 'Failed to fetch conversation', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) {
        setChatInput(content);
        setChatTitle(file.name.replace(/\.[^/.]+$/, ''));
        if (onNotify) onNotify(`Loaded "${file.name}"`, 'info');
      }
    };
    reader.readAsText(file);
  };

  // Prepare chart data
  const chartData = currentConversation?.messages.map((m, idx) => ({
    name: `#${idx + 1}`,
    speaker: m.speaker,
    toxicity: m.toxicity_score,
    label: m.label
  })) || [];

  const getToxicityBadge = (score: number, label: string) => {
    if (score < 30 && label === 'Safe') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-safe/10 border border-safe/30 text-safe">
          <CheckCircle2 className="w-3 h-3" />
          {score.toFixed(1)}% Safe
        </span>
      );
    } else if (score <= 60 || label === 'Caution') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-caution/10 border border-caution/30 text-caution">
          <AlertTriangle className="w-3 h-3" />
          {score.toFixed(1)}% Caution
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-toxic/10 border border-toxic/30 text-toxic">
          <Flame className="w-3 h-3" />
          {score.toFixed(1)}% Toxic
        </span>
      );
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white font-sans">
          Conversation Dynamics
        </h1>
        <p className="text-muted text-sm mt-1">
          Paste a chat thread ("Name: message") or upload a transcript to monitor escalation and detect hostility.
        </p>
      </div>

      {/* Input Section */}
      <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-xl space-y-4">
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <input
            type="text"
            value={chatTitle}
            onChange={(e) => setChatTitle(e.target.value)}
            placeholder="Conversation Title (optional)"
            className="bg-[#18181c] border border-cardBorder px-3.5 py-1.5 rounded-lg text-sm text-white placeholder-muted focus:outline-none w-full sm:w-80 font-mono"
          />

          <label className="flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg border border-cardBorder bg-[#18181c] hover:bg-[#222228] text-xs font-mono text-neutral-300 cursor-pointer transition-colors self-start sm:self-auto">
            <Upload className="w-3.5 h-3.5 text-brand" />
            <span>Upload .txt Chat</span>
            <input
              type="file"
              accept=".txt,.log"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>

        <textarea
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder={`Alice: Hey team, how is the project going?\nBob: Did you even read the docs?\nCharlie: Stop being rude Bob.`}
          rows={6}
          className="w-full bg-[#141417] border border-cardBorder rounded-lg p-3 text-white placeholder-muted/50 font-mono text-xs focus:outline-none resize-none leading-relaxed"
        />

        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => {
              setChatInput(DEFAULT_CHAT_SAMPLE);
              setChatTitle('Sample Slack Thread');
            }}
            className="text-xs text-muted hover:text-brand underline font-mono cursor-pointer"
          >
            Reset to sample thread
          </button>

          <button
            onClick={handleProcessChat}
            disabled={isProcessing || !chatInput.trim()}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-semibold font-mono transition-all shadow-md shadow-brand/20 disabled:opacity-50 cursor-pointer"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Analyze Conversation</span>
                <MessageSquare className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

      </div>

      {/* Results Section */}
      {currentConversation && (
        <div className="space-y-6">
          
          {/* Conversation Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            
            <div className="p-4 rounded-xl bg-card border border-cardBorder">
              <span className="text-[10px] font-mono text-muted uppercase tracking-wider block">
                Total Messages
              </span>
              <span className="text-2xl font-bold font-mono text-white mt-1 block">
                {currentConversation.message_count}
              </span>
            </div>

            <div className="p-4 rounded-xl bg-card border border-cardBorder">
              <span className="text-[10px] font-mono text-muted uppercase tracking-wider block">
                Avg Toxicity
              </span>
              <span className="text-2xl font-bold font-mono text-brand mt-1 block">
                {currentConversation.avg_toxicity.toFixed(1)}%
              </span>
            </div>

            <div className="p-4 rounded-xl bg-card border border-cardBorder">
              <span className="text-[10px] font-mono text-muted uppercase tracking-wider block">
                Most Toxic Speaker
              </span>
              <span className="text-lg font-bold font-mono text-toxic mt-1 block truncate">
                {currentConversation.most_toxic_speaker}
              </span>
            </div>

            <div className="p-4 rounded-xl bg-card border border-cardBorder">
              <span className="text-[10px] font-mono text-muted uppercase tracking-wider block">
                Escalation Trend
              </span>
              <div className="flex items-center gap-1.5 mt-1">
                <TrendingUp className="w-4 h-4 text-brand" />
                <span className="text-sm font-bold font-mono text-white">
                  {currentConversation.escalation_trend}
                </span>
              </div>
            </div>

          </div>

          {/* Line Chart of Toxicity Across Conversation */}
          <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white font-sans">
                  Conversation Toxicity Progression
                </h3>
                <p className="text-xs text-muted">
                  Per-message toxicity curve across dialogue chronology
                </p>
              </div>
              <span className="text-xs font-mono text-brand">Threshold: 30% Caution</span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222226" />
                  <XAxis dataKey="name" stroke="#8a8a93" fontSize={11} fontStyle="JetBrains Mono" />
                  <YAxis domain={[0, 100]} stroke="#8a8a93" fontSize={11} fontStyle="JetBrains Mono" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#161619',
                      border: '1px solid #222226',
                      borderRadius: '8px',
                      fontFamily: 'JetBrains Mono',
                      fontSize: '12px'
                    }}
                    formatter={(val: any) => [`${val}%`, 'Toxicity']}
                    labelFormatter={(label) => `Message ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="toxicity"
                    stroke="#ff6a1a"
                    strokeWidth={2.5}
                    dot={{ fill: '#ff6a1a', r: 4 }}
                    activeDot={{ r: 6, fill: '#fff', stroke: '#ff6a1a' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Message List */}
          <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl space-y-3">
            <h3 className="text-sm font-bold text-white font-sans mb-3">
              Parsed Message Stream ({currentConversation.messages.length})
            </h3>

            <div className="space-y-2.5">
              {currentConversation.messages.map((msg, idx) => (
                <div
                  key={msg.id || idx}
                  className="p-3.5 rounded-lg bg-[#141417] border border-cardBorder flex flex-col sm:flex-row sm:items-start justify-between gap-3 transition-colors hover:border-cardBorder/80"
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="w-7 h-7 rounded-full bg-[#202025] flex items-center justify-center text-muted font-bold text-xs flex-shrink-0">
                      {msg.speaker.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-white font-mono">{msg.speaker}</span>
                        <span className="text-[10px] text-muted font-mono">#{idx + 1}</span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-cardBorder text-neutral-300 font-mono">
                          {msg.tone}
                        </span>
                      </div>
                      <p className="text-xs text-neutral-300 font-sans mt-1 break-words">
                        {msg.text}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center self-end sm:self-center flex-shrink-0">
                    {getToxicityBadge(msg.toxicity_score, msg.label)}
                  </div>
                </div>
              ))}
            </div>

          </div>

        </div>
      )}

      {/* History List */}
      {historyList.length > 0 && (
        <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <History className="w-4 h-4 text-brand" />
            <h3 className="text-sm font-bold text-white font-sans">
              Previous Analyzed Conversations
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {historyList.map((hist) => (
              <div
                key={hist.id}
                onClick={() => handleSelectHistory(hist.id)}
                className="p-3.5 rounded-lg bg-[#141417] border border-cardBorder hover:border-brand/40 transition-colors cursor-pointer space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-white font-mono truncate max-w-[180px]">
                    {hist.title}
                  </span>
                  <span className="text-[10px] text-brand font-mono font-bold">
                    {hist.avg_toxicity.toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-[10px] text-muted font-mono pt-1">
                  <span>{hist.message_count} messages</span>
                  <span>Speaker: {hist.most_toxic_speaker}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
