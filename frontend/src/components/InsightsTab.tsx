import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingDown,
  Activity,
  Layers,
  Sparkles,
  PieChart as PieIcon,
  RefreshCw,
  Hash
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';
import { InsightsResponse } from '../types';
import { fetchInsights } from '../api/client';

const TONE_COLORS: Record<string, string> = {
  Polite: '#2ee6a6',
  Friendly: '#38bdf8',
  Neutral: '#8a8a93',
  'Sarcastic-ish/Passive-aggressive': '#a855f7',
  Rude: '#f59e0b',
  Aggressive: '#ef4444'
};

export const InsightsTab: React.FC = () => {
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const data = await fetchInsights();
      setInsights(data);
    } catch (err) {
      console.error('Failed to load insights data', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (isLoading && !insights) {
    return (
      <div className="max-w-[1000px] mx-auto px-4 py-16 text-center space-y-3">
        <RefreshCw className="w-8 h-8 text-brand animate-spin mx-auto" />
        <p className="text-sm text-muted font-mono">Aggregating telemetry and intelligence metrics...</p>
      </div>
    );
  }

  // Fallback default structure if DB has zero entries yet
  const data = insights || {
    total_analyzed: 0,
    avg_toxicity: 0,
    category_distribution: { toxic: 0, insult: 0, harassment: 0, obscene: 0, threat: 0, identity_attack: 0 },
    tone_distribution: { Neutral: 1 },
    toxicity_over_time: [],
    top_flagged_words: [],
    rewrite_improvement_avg: 0,
    total_rewrites: 0
  };

  // Prepare Category Bar Data
  const categoryChartData = [
    { name: 'Toxic', score: data.category_distribution.toxic || 0 },
    { name: 'Insult', score: data.category_distribution.insult || 0 },
    { name: 'Harassment', score: data.category_distribution.harassment || 0 },
    { name: 'Obscene', score: data.category_distribution.obscene || 0 },
    { name: 'Threat', score: data.category_distribution.threat || 0 },
    { name: 'Identity Attack', score: data.category_distribution.identity_attack || 0 },
  ];

  // Prepare Tone Donut Data
  const toneChartData = Object.entries(data.tone_distribution)
    .filter(([_, count]) => count > 0)
    .map(([tone, count]) => ({
      name: tone,
      value: count,
      color: TONE_COLORS[tone] || '#ff6a1a'
    }));

  // Rewrite Comparison Bar Data
  const rewriteComparisonData = [
    {
      name: 'Toxicity Level',
      Original: Number((data.avg_toxicity || 42.5).toFixed(1)),
      Rewritten: Number(Math.max(0.5, (data.avg_toxicity - data.rewrite_improvement_avg)).toFixed(1))
    }
  ];

  return (
    <div className="max-w-[1000px] mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white font-sans">
            Aggregate Insights
          </h1>
          <p className="text-muted text-sm mt-1">
            Real-time analytics across all evaluated communications and constructive rewrites.
          </p>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-cardBorder bg-card hover:bg-cardHover text-xs font-mono text-neutral-300 transition-colors self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5 text-brand" />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* Top 3 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        
        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-muted font-bold">
              Messages Analyzed
            </span>
            <Activity className="w-4 h-4 text-brand" />
          </div>
          <div className="text-3xl font-bold font-mono text-white mt-2">
            {data.total_analyzed}
          </div>
          <p className="text-xs text-muted mt-1">
            Across single queries & team transcripts
          </p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-muted font-bold">
              Mean Toxicity
            </span>
            <Layers className="w-4 h-4 text-caution" />
          </div>
          <div className="text-3xl font-bold font-mono text-caution mt-2">
            {data.avg_toxicity.toFixed(1)}%
          </div>
          <p className="text-xs text-muted mt-1">
            Dataset baseline average score
          </p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-muted font-bold">
              Rewrites Generated
            </span>
            <Sparkles className="w-4 h-4 text-safe" />
          </div>
          <div className="text-3xl font-bold font-mono text-safe mt-2">
            {data.total_rewrites}
          </div>
          <p className="text-xs text-muted mt-1">
            Avg drop: <span className="text-safe font-mono font-bold">-{data.rewrite_improvement_avg.toFixed(1)}%</span>
          </p>
        </div>

      </div>

      {/* Charts Grid: Row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Category Averages Bar Chart */}
        <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-sans flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-brand" />
              Category Averages (%)
            </h3>
            <p className="text-xs text-muted">Distribution across 6 monitored risk categories</p>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -15, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222226" vertical={false} />
                <XAxis dataKey="name" stroke="#8a8a93" fontSize={10} fontStyle="JetBrains Mono" interval={0} angle={-20} textAnchor="end" />
                <YAxis domain={[0, 100]} stroke="#8a8a93" fontSize={11} fontStyle="JetBrains Mono" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#161619',
                    border: '1px solid #222226',
                    borderRadius: '8px',
                    fontFamily: 'JetBrains Mono',
                    fontSize: '12px'
                  }}
                  formatter={(val: any) => [`${val}%`, 'Average']}
                />
                <Bar dataKey="score" fill="#ff6a1a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tone Distribution Donut Chart */}
        <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-sans flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-brand" />
              Tone Distribution
            </h3>
            <p className="text-xs text-muted">Observed communication styles across messages</p>
          </div>

          <div className="h-60 w-full flex items-center justify-center">
            {toneChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={toneChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {toneChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="#111113" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#161619',
                      border: '1px solid #222226',
                      borderRadius: '8px',
                      fontFamily: 'JetBrains Mono',
                      fontSize: '12px'
                    }}
                    formatter={(val: any, name: any) => [`${val} messages`, name]}
                  />
                  <Legend
                    layout="horizontal"
                    verticalAlign="bottom"
                    align="center"
                    wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono', paddingTop: '10px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-muted font-mono">No tone data recorded yet.</div>
            )}
          </div>
        </div>

      </div>

      {/* Charts Grid: Row 2 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Toxicity Over Time Line Chart */}
        <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-sans flex items-center gap-2">
              <Activity className="w-4 h-4 text-brand" />
              Toxicity Over Time
            </h3>
            <p className="text-xs text-muted">Chronological trend of recently scored queries</p>
          </div>

          <div className="h-60 w-full">
            {data.toxicity_over_time.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.toxicity_over_time} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222226" />
                  <XAxis dataKey="timestamp" stroke="#8a8a93" fontSize={10} fontStyle="JetBrains Mono" />
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
                  />
                  <Line type="monotone" dataKey="toxicity_score" stroke="#2ee6a6" strokeWidth={2.5} dot={{ r: 3, fill: '#2ee6a6' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-muted font-mono">
                Analyze more messages to populate timeline trend.
              </div>
            )}
          </div>
        </div>

        {/* Before vs After Rewrite Comparison Bar */}
        <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-sans flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-safe" />
              Before vs After Rewrite Impact
            </h3>
            <p className="text-xs text-muted">Average toxicity reduction across suggested reframings</p>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rewriteComparisonData} margin={{ top: 15, right: 20, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222226" vertical={false} />
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
                  formatter={(val: any) => [`${val}%`, '']}
                />
                <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono', paddingTop: '8px' }} />
                <Bar dataKey="Original" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Rewritten" fill="#2ee6a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Top Flagged Words Cloud / Table */}
      {data.top_flagged_words && data.top_flagged_words.length > 0 && (
        <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <Hash className="w-4 h-4 text-brand" />
            <h3 className="text-sm font-bold text-white font-sans">
              Frequently Flagged Hostile Terms
            </h3>
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            {data.top_flagged_words.map((fw, idx) => (
              <div
                key={idx}
                className="px-3 py-1.5 rounded-lg bg-[#18181c] border border-cardBorder flex items-center gap-2 text-xs font-mono"
              >
                <span className="text-white font-semibold">"{fw.word}"</span>
                <span className="px-1.5 py-0.2 rounded bg-brand/10 text-brand border border-brand/20 text-[10px]">
                  {fw.count}x
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};

