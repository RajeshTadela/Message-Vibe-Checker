import {
  AnalyzeResponse,
  RewriteResponse,
  ConversationDetail,
  ConversationSummary,
  InsightsResponse,
  SampleItem
} from '../types';

const API_BASE = '';

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === 'online';
  } catch {
    return false;
  }
}

export async function fetchSamples(): Promise<SampleItem[]> {
  const res = await fetch(`${API_BASE}/samples`);
  if (!res.ok) throw new Error('Failed to load sample messages');
  return res.json();
}

export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail || 'Analysis request failed');
  }
  return res.json();
}

export async function rewriteText(text: string, mode: string): Promise<RewriteResponse> {
  const res = await fetch(`${API_BASE}/rewrite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, mode })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Rewrite failed' }));
    throw new Error(err.detail || 'Rewrite request failed');
  }
  return res.json();
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${API_BASE}/conversations`);
  if (!res.ok) throw new Error('Failed to fetch conversations');
  return res.json();
}

export async function fetchConversation(id: number): Promise<ConversationDetail> {
  const res = await fetch(`${API_BASE}/conversations/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch conversation #${id}`);
  return res.json();
}

export async function createConversation(chat_text: string, title?: string): Promise<ConversationDetail> {
  const res = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_text, title })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to process conversation' }));
    throw new Error(err.detail || 'Conversation creation failed');
  }
  return res.json();
}

export async function fetchInsights(): Promise<InsightsResponse> {
  const res = await fetch(`${API_BASE}/insights`);
  if (!res.ok) throw new Error('Failed to fetch insights');
  return res.json();
}

