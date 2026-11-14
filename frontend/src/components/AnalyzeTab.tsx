import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Shield,
  ArrowRight,
  ArrowDown,
  Copy,
  Check,
  AlertTriangle,
  ShieldCheck,
  Flame,
  Info,
  RefreshCw,
  Sliders
} from 'lucide-react';
import {
  AnalyzeResponse,
  RewriteResponse,
  SampleItem,
  CategoryScores,
  FlaggedToken
} from '../types';
import { analyzeText, rewriteText, fetchSamples } from '../api/client';

interface AnalyzeTabProps {
  onNotify?: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

const CATEGORY_LABELS: { key: keyof CategoryScores; label: string; description: string }[] = [
  { key: 'toxic', label: 'Toxic', description: 'Rude, disrespectful, or unreasonable language.' },
  { key: 'insult', label: 'Insult', description: 'Disparaging, derogatory, or demeaning statements.' },
  { key: 'harassment', label: 'Harassment', description: 'Targeted hostile badgering or intimidatory phrasing.' },
  { key: 'obscene', label: 'Obscene', description: 'Vulgar, profane, or inappropriate expressions.' },
  { key: 'threat', label: 'Threat', description: 'Statements suggesting intention to inflict harm.' },
  { key: 'identity_attack', label: 'Identity Attack', description: 'Negative or hostile comments based on identity.' },
];

export const AnalyzeTab: React.FC<AnalyzeTabProps> = ({ onNotify }) => {
  const [text, setText] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isRewriting, setIsRewriting] = useState<boolean>(false);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [rewriteMode, setRewriteMode] = useState<'Constructive' | 'Professional' | 'Friendly' | 'Neutral'>('Constructive');
  const [rewriteResult, setRewriteResult] = useState<RewriteResponse | null>(null);
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [copied, setCopied] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch samples on mount
  useEffect(() => {
    fetchSamples()
      .then(setSamples)
      .catch((err) => console.error('Failed to load samples', err));
  }, []);

  const handleAnalyze = async (textToAnalyze?: string) => {
    const targetText = (textToAnalyze !== undefined ? textToAnalyze : text).trim();
    if (!targetText) {
      setErrorMsg('Please enter a message to analyze.');
      return;
    }
    if (targetText.length > 1000) {
      setErrorMsg('Text exceeds maximum limit of 1000 characters.');
      return;
    }

    setErrorMsg(null);
    setIsAnalyzing(true);
    try {
      const data = await analyzeText(targetText);
      setAnalysis(data);

      // Automatically generate a rewrite if text has toxicity or is non-safe
      handleRewrite(targetText, rewriteMode);
    } catch (err: any) {
      setErrorMsg(err.message || 'Analysis failed. Please ensure the backend is running.');
      if (onNotify) onNotify(err.message, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRewrite = async (targetText: string, mode: 'Constructive' | 'Professional' | 'Friendly' | 'Neutral') => {
    if (!targetText.trim()) return;
    setIsRewriting(true);
    try {
      const res = await rewriteText(targetText, mode);
      setRewriteResult(res);
    } catch (err: any) {
      console.error('Rewrite generation failed', err);
    } finally {
      setIsRewriting(false);
    }
  };

  const handleModeChange = (newMode: 'Constructive' | 'Professional' | 'Friendly' | 'Neutral') => {
    setRewriteMode(newMode);
    if (text.trim()) {
      handleRewrite(text.trim(), newMode);
    }
  };

  const handleSampleClick = (sampleText: string) => {
    setText(sampleText);
    setErrorMsg(null);
    handleAnalyze(sampleText);
  };

  const handleCopyRewrite = () => {
    if (!rewriteResult) return;
    navigator.clipboard.writeText(rewriteResult.rewrite);
    setCopied(true);
    if (onNotify) onNotify('Copied suggestion to clipboard!', 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReplaceMessage = () => {
    if (!rewriteResult) return;
    const replacement = rewriteResult.rewrite;
    setText(replacement);
    if (onNotify) onNotify('Message replaced with rewrite! Re-analyzing...', 'info');
    handleAnalyze(replacement);
  };

  // Helper for status badge styling
  const getBadgeStyle = (label: string) => {
    switch (label) {
      case 'Safe':
        return {
          pillBg: 'bg-safe/10 text-safe border-safe/30',
          textColor: 'text-safe',
          icon: <ShieldCheck className="w-4 h-4 stroke-[2.2]" />,
          textLabel: 'Safe ✓'
        };
      case 'Caution':
        return {
          pillBg: 'bg-caution/10 text-caution border-caution/30',
          textColor: 'text-caution',
          icon: <AlertTriangle className="w-4 h-4 stroke-[2.2]" />,
          textLabel: 'Caution'
        };
      case 'Toxic':
      default:
        return {
          pillBg: 'bg-toxic/10 text-toxic border-toxic/30',
          textColor: 'text-toxic',
          icon: <Flame className="w-4 h-4 stroke-[2.2]" />,
          textLabel: 'Toxic'
        };
    }
  };

  // Render text with highlighted flagged tokens
  const renderHighlightedText = (content: string, tokens: FlaggedToken[]) => {
    if (!tokens || tokens.length === 0) return <span>{content}</span>;

    const words = content.split(/(\s+|[.,!?;])/);
    const tokenMap = new Map(tokens.map((t) => [t.token.toLowerCase(), t.weight]));

    return (
      <span>
        {words.map((chunk, idx) => {
          const lower = chunk.toLowerCase();
          const weight = tokenMap.get(lower);
          if (weight !== undefined) {
            return (
              <span
                key={idx}
                className="relative group inline-block text-toxic font-semibold border-b-2 border-toxic/80 bg-toxic/10 px-0.5 rounded cursor-help"
              >
                {chunk}
                <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block px-2 py-1 rounded bg-[#1e1e24] border border-cardBorder text-[10px] text-white font-mono shadow-xl whitespace-nowrap z-30">
                  Flagged: {chunk} (impact: {(weight * 100).toFixed(0)}%)
                </span>
              </span>
            );
          }
          return <span key={idx}>{chunk}</span>;
        })}
      </span>
    );
  };

  return (
    <div className="max-w-[1000px] mx-auto px-4 py-8 space-y-6">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white font-sans">
          Analyze a message
        </h1>
        <p className="text-muted text-sm mt-1">
          Check how your message may come across before sending it.
        </p>
      </div>

      {/* Main Input Textarea Card */}
      <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-xl relative transition-card hover:border-cardBorder/80">
        <textarea
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            if (errorMsg) setErrorMsg(null);
          }}
          placeholder="Type or paste a message to evaluate its tone, toxicity, and impact..."
          rows={4}
          maxLength={1000}
          className="w-full bg-transparent text-white placeholder-muted/60 text-base focus:outline-none resize-none leading-relaxed font-sans"
        />

        {/* Textarea Bottom Controls */}
        <div className="mt-4 pt-3 border-t border-cardBorder/60 flex items-center justify-between">
          <div className="text-xs font-mono text-muted">
            <span className={text.length > 900 ? 'text-caution font-semibold' : ''}>
              {text.length}
            </span>
            <span className="opacity-70"> / 1000 characters</span>
          </div>

          <button
            onClick={() => handleAnalyze()}
            disabled={isAnalyzing || !text.trim()}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-semibold transition-all shadow-md shadow-brand/20 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <span>Analyze message</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Sample Links Bar */}
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted pt-1">
        <span className="font-medium text-white/70">Try sample:</span>
        {samples.length > 0 ? (
          samples.map((s, idx) => (
            <React.Fragment key={s.id}>
              <button
                onClick={() => handleSampleClick(s.text)}
                className="underline underline-offset-4 hover:text-brand transition-colors cursor-pointer text-left font-mono"
              >
                Sample {idx + 1} ({s.category})
              </button>
              {idx < samples.length - 1 && <span className="opacity-40">·</span>}
            </React.Fragment>
          ))
        ) : (
          <span className="opacity-60">Loading samples...</span>
        )}
      </div>

      {/* Error Message Toast */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-toxic/10 border border-toxic/30 text-toxic text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Loading Skeleton */}
      {isAnalyzing && (
        <div className="p-6 rounded-xl bg-card border border-cardBorder animate-pulse space-y-4">
          <div className="h-4 w-28 bg-subtle rounded" />
          <div className="h-16 w-48 bg-subtle rounded" />
          <div className="h-4 w-full bg-subtle rounded" />
        </div>
      )}

      {/* Analysis Results Display */}
      {analysis && !isAnalyzing && (
        <div className="space-y-6">
          
          {/* Main Result Card */}
          <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-2xl transition-card">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              
              {/* Left: Toxicity % and status badge */}
              <div>
                <span className="text-[11px] font-mono uppercase tracking-wider text-muted font-bold">
                  TOXICITY RESULT
                </span>
                <div className="flex items-baseline gap-4 mt-1">
                  <div className={`text-5xl md:text-6xl font-bold font-mono tracking-tight ${getBadgeStyle(analysis.label).textColor}`}>
                    {analysis.toxicity_score.toFixed(1)}%
                  </div>
                  <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold font-mono border ${getBadgeStyle(analysis.label).pillBg}`}>
                    {getBadgeStyle(analysis.label).icon}
                    <span>{getBadgeStyle(analysis.label).textLabel}</span>
                  </div>
                </div>
              </div>

              {/* Right: Detected Tone Box */}
              <div className="bg-[#17171a] p-3.5 rounded-xl border border-cardBorder flex items-center gap-3 self-start md:self-auto">
                <Sliders className="w-4 h-4 text-brand" />
                <div className="text-sm">
                  <span className="text-muted">Detected Tone: </span>
                  <span className="font-bold text-white font-sans">{analysis.tone}</span>
                </div>
              </div>

            </div>

            {/* Explanation sentence below */}
            <p className="mt-4 pt-4 border-t border-cardBorder/60 text-sm text-neutral-300 flex items-center gap-2">
              <Info className="w-4 h-4 text-brand flex-shrink-0" />
              <span>{analysis.explanation || 'Probabilistic classification based on multi-label toxicity patterns.'}</span>
            </p>
          </div>

          {/* Multi-Category Scores */}
          <div className="p-6 rounded-xl bg-card border border-cardBorder shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[11px] font-mono uppercase tracking-wider text-muted font-bold">
                MULTI-CATEGORY SCORES
              </span>
              <span className="text-xs text-muted font-mono">Normalized Probabilities</span>
            </div>

            <div className="space-y-4">
              {CATEGORY_LABELS.map(({ key, label }) => {
                const val = analysis.categories[key] || 0;
                const isHigh = val > 50;
                const isMedium = val >= 25 && val <= 50;
                
                return (
                  <div key={key} className="space-y-1.5">
                    <div className="flex justify-between items-center text-xs font-mono">
                      <span className="text-neutral-300 font-medium">{label}</span>
                      <span className={isHigh ? 'text-toxic font-bold' : isMedium ? 'text-caution' : 'text-neutral-400'}>
                        {val.toFixed(1)}%
                      </span>
                    </div>
                    {/* Thin animated horizontal bar */}
                    <div className="w-full h-1.5 bg-subtle rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ease-out ${
                          isHigh ? 'bg-toxic' : isMedium ? 'bg-caution' : 'bg-brand'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(val, 0.5))}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Flagged Tokens Warning (if any) */}
          {analysis.flagged_tokens && analysis.flagged_tokens.length > 0 && (
            <div className="p-4 rounded-xl bg-toxic/5 border border-toxic/20 text-xs text-neutral-300 flex flex-wrap items-center gap-2">
              <span className="font-mono text-toxic font-semibold uppercase tracking-wider">
                Flagged Words:
              </span>
              {analysis.flagged_tokens.map((t, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded bg-toxic/10 text-toxic border border-toxic/30 font-mono"
                >
                  "{t.token}" ({(t.weight * 100).toFixed(0)}%)
                </span>
              ))}
            </div>
          )}

          {/* Rewrite Card "ToxicBuddy Suggests" */}
          <div className="p-6 rounded-xl bg-card border border-brand/40 shadow-2xl relative overflow-hidden">
            
            {/* Top Row: Title + Segmented Control */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-cardBorder">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-brand/10 border border-brand/30 flex items-center justify-center text-brand">
                  <Sparkles className="w-4 h-4 fill-brand/20 stroke-brand" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white font-sans flex items-center gap-2">
                    ToxicBuddy Suggests
                  </h3>
                  <p className="text-xs text-muted">
                    Reframing message intent into constructive language
                  </p>
                </div>
              </div>

              {/* Segmented Mode Selector */}
              <div className="flex items-center p-1 rounded-lg bg-[#18181c] border border-cardBorder self-start sm:self-auto">
                {(['Constructive', 'Professional', 'Friendly', 'Neutral'] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => handleModeChange(m)}
                    className={`px-3 py-1 text-xs font-mono rounded-md transition-all cursor-pointer ${
                      rewriteMode === m
                        ? 'bg-brand text-white font-bold shadow-sm'
                        : 'text-muted hover:text-white'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>

            {/* Rewrite Content Comparison */}
            <div className="mt-5 space-y-4">
              
              {/* Original Message Box */}
              <div>
                <span className="text-[10px] uppercase font-mono tracking-wider text-muted font-bold block mb-1.5">
                  YOUR ORIGINAL MESSAGE
                </span>
                <div className="p-4 rounded-lg bg-[#161619] border border-cardBorder font-mono text-sm text-neutral-300 leading-relaxed">
                  {renderHighlightedText(text, analysis.flagged_tokens)}
                </div>
              </div>

              {/* Down Arrow Indicator */}
              <div className="flex justify-center -my-1">
                <div className="w-6 h-6 rounded-full bg-card border border-cardBorder flex items-center justify-center text-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Suggested Rewrite Box */}
              <div>
                <span className="text-[10px] uppercase font-mono tracking-wider text-brand font-bold block mb-1.5">
                  SUGGESTED REWRITE ({rewriteMode.toUpperCase()})
                </span>
                <div className="p-4 rounded-lg bg-brand/5 border border-brand/50 font-mono text-sm text-white leading-relaxed relative">
                  {isRewriting ? (
                    <div className="flex items-center gap-2 text-muted py-1">
                      <RefreshCw className="w-4 h-4 animate-spin text-brand" />
                      <span>Generating polite rewrite...</span>
                    </div>
                  ) : rewriteResult ? (
                    <span>{rewriteResult.rewrite}</span>
                  ) : (
                    <span className="text-muted">No rewrite available yet.</span>
                  )}
                </div>
              </div>

              {/* Rewrite Score Chips + Action Buttons */}
              {rewriteResult && !isRewriting && (
                <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
                  
                  {/* Quality Metric Chips */}
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="px-2.5 py-1 rounded bg-safe/10 border border-safe/30 text-safe">
                      New Toxicity: {rewriteResult.new_toxicity_score.toFixed(1)}%
                    </span>
                    <span className="px-2.5 py-1 rounded bg-[#222228] border border-cardBorder text-neutral-300">
                      Meaning Match: {(rewriteResult.similarity * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleCopyRewrite}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-cardBorder bg-[#18181c] hover:bg-[#222228] text-white text-xs font-mono transition-colors cursor-pointer"
                    >
                      {copied ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-safe" />
                          <span className="text-safe">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-muted" />
                          <span>Copy rewrite</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={handleReplaceMessage}
                      className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-semibold transition-all shadow-sm cursor-pointer"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>Replace message</span>
                    </button>
                  </div>

                </div>
              )}

            </div>

          </div>

        </div>
      )}

      {/* Empty State when no analysis performed */}
      {!analysis && !isAnalyzing && (
        <div className="py-12 text-center rounded-xl border border-dashed border-cardBorder p-8">
          <Shield className="w-10 h-10 text-muted/40 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No message analyzed yet</h3>
          <p className="text-xs text-muted max-w-sm mx-auto mt-1">
            Type your message above or click one of the preset samples to inspect real-time toxicity scores and suggested constructive alternatives.
          </p>
        </div>
      )}

    </div>
  );
};
