export interface CategoryScores {
  toxic: number;
  insult: number;
  harassment: number;
  obscene: number;
  threat: number;
  identity_attack: number;
}

export interface FlaggedToken {
  token: string;
  weight: number;
}

export interface AnalyzeResponse {
  toxicity_score: number;
  label: 'Safe' | 'Caution' | 'Toxic';
  tone: string;
  categories: CategoryScores;
  char_count: number;
  flagged_tokens: FlaggedToken[];
  explanation?: string;
}

export interface RewriteResponse {
  original: string;
  rewrite: string;
  mode: 'Constructive' | 'Professional' | 'Friendly' | 'Neutral';
  new_toxicity_score: number;
  similarity: number;
}

export interface ConversationMessage {
  id?: number;
  speaker: string;
  text: string;
  toxicity_score: number;
  label: string;
  tone: string;
  order_index: number;
}

export interface ConversationSummary {
  id: number;
  title: string;
  message_count: number;
  avg_toxicity: number;
  most_toxic_speaker: string;
  escalation_trend: string;
  created_at: string;
}

export interface ConversationDetail extends ConversationSummary {
  raw_text: string;
  messages: ConversationMessage[];
}

export interface ToxicityPoint {
  timestamp: string;
  toxicity_score: number;
  label: string;
}

export interface FlaggedWordStat {
  word: string;
  count: number;
}

export interface InsightsResponse {
  total_analyzed: number;
  avg_toxicity: number;
  category_distribution: Record<string, number>;
  tone_distribution: Record<string, number>;
  toxicity_over_time: ToxicityPoint[];
  top_flagged_words: FlaggedWordStat[];
  rewrite_improvement_avg: number;
  total_rewrites: number;
}

export interface SampleItem {
  id: string;
  title: string;
  category: string;
  text: string;
  expected_tone: string;
  expected_label: string;
}

