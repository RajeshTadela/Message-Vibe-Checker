# VibeCheck — Tone Checker: Toxicity & Tone Intelligence Platform

<div align="center">

```
  ██╗   ██╗██╗██████╗ ███████╗ ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
  ██║   ██║██║██╔══██╗██╔════╝██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
  ██║   ██║██║██████╔╝█████╗  ██║     ███████║█████╗  ██║     █████╔╝ 
  ╚██╗ ██╔╝██║██╔══██╗██╔══╝  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
   ╚████╔╝ ██║██████╔╝███████╗╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
    ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
                        Tone  Checker  v1.0
```

**Analyze · Understand · Improve**

A developer-grade full-stack NLP platform that analyzes how a message may come across before it's sent — scoring toxicity across 6 categories, detecting tone, and rewriting it in 4 constructive styles.

</div>

---

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                    Browser (React + Vite + TS)                    │
│   ┌──────────┐  ┌────────────────┐  ┌──────────────────────────┐  │
│   │ Analyze  │  │ Conversations  │  │  Insights (Recharts)     │  │
│   │ Tab      │  │ Tab            │  │  Stats + Charts          │  │
│   │ (input   │  │ (chat paste    │  │  Tone donut, Category    │  │
│   │ + charts │  │ + timeline)    │  │  bar, Timeline, Rewrites)│  │
│   └──────────┘  └────────────────┘  └──────────────────────────┘  │
│                     Vite DevServer :5173                           │
└────────────────────────────┬──────────────────────────────────────┘
              REST API Proxy │
┌────────────────────────────▼──────────────────────────────────────┐
│                   FastAPI + Uvicorn  :8000                         │
│   ┌──────────┐   ┌──────────┐  ┌────────────┐  ┌───────────────┐  │
│   │ /analyze │   │ /rewrite │  │/conversations│  │   /insights   │  │
│   └────┬─────┘   └────┬─────┘  └──────┬─────┘  └───────┬───────┘  │
│        │              │                │                 │           │
│   ┌────▼──────────────▼────────────────▼─────────────────▼──────┐  │
│   │                  ML Container (singleton at startup)          │  │
│   │  ┌──────────────────┐    ┌──────────────────────────────┐   │  │
│   │  │ ToxicityService  │    │   RewriterEngine             │   │  │
│   │  │ (unitary/toxic-  │    │   (Template + Semantic       │   │  │
│   │  │  bert inference) │    │    Similarity Scoring)       │   │  │
│   │  │ + ToneClassifier │    │   sentence-transformers      │   │  │
│   │  │   (rule-based)   │    │   all-MiniLM-L6-v2          │   │  │
│   │  └──────────────────┘    └──────────────────────────────┘   │  │
│   └───────────────────────────────────────────────────────────────┘  │
│                     SQLAlchemy / SQLite                            │
└───────────────────────────────────────────────────────────────────┘
            /data           /ml/artifacts          /ml/reports
```

---

## Project Structure

```
c:/nlp/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS + router registration
│   │   ├── config.py        # Pydantic settings
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # DB table definitions (Analysis, Rewrite, Conversation)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── routes/
│   │   │   ├── health.py    # GET /health
│   │   │   ├── analyze.py   # POST /analyze
│   │   │   ├── rewrite.py   # POST /rewrite
│   │   │   ├── conversations.py  # POST|GET /conversations
│   │   │   ├── insights.py  # GET /insights
│   │   │   └── samples.py   # GET /samples
│   │   └── services/
│   │       └── ml_singleton.py  # Lazy-loaded ML container
│   ├── tests/
│   │   ├── test_api.py          # 9 API integration tests
│   │   └── test_rewrite_rules.py # 3 rewrite unit tests (inc. verbatim check)
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # ReactDOM.createRoot
│   │   ├── App.tsx              # App shell, toast, health polling
│   │   ├── index.css            # Tailwind directives + custom scrollbar
│   │   ├── api/client.ts        # API fetch wrapper
│   │   ├── types/index.ts       # TypeScript interfaces
│   │   └── components/
│   │       ├── TopBar.tsx        # Nav header with logo + tabs + status pill
│   │       ├── AnalyzeTab.tsx    # Main analysis UI with rewrite card
│   │       ├── ConversationsTab.tsx # Chat parser + timeline chart
│   │       └── InsightsTab.tsx   # Aggregate charts + stats
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── smoke_test.py            # Frontend build smoke test
├── ml/
│   ├── prepare_data.py          # Synthetic benchmark corpus generator (254 samples)
│   ├── train_baseline.py        # TF-IDF + Logistic Regression training + ROC-AUC eval
│   ├── train_distilbert.py      # DistilBERT fine-tuning script (run on GPU)
│   ├── train_colab.ipynb        # Google Colab GPU training notebook
│   ├── tone_classifier.py       # Rule-based 6-tone classifier
│   ├── toxicity_service.py      # Toxicity inference wrapper (unitary/toxic-bert)
│   ├── rewriter.py              # 4-mode semantic rewriter with similarity scoring
│   ├── eval_rewrite.py          # 200-sample rewrite evaluation script
│   ├── bias_check.py            # Identity bias false-positive rate assessment
│   ├── download_models.py       # Pre-download HuggingFace model weights
│   ├── artifacts/
│   │   ├── baseline_model.joblib    # Trained TF-IDF + LR model artifacts
│   │   └── thresholds.json          # Per-category tuned decision thresholds
│   └── reports/
│       ├── toxicity_metrics.md      # Per-label ROC-AUC, F1, P, R, Thresholds
│       ├── rewrite_eval.md          # 200-sample rewrite evaluation results
│       └── bias.md                  # Identity demographic bias analysis
├── data/
│   └── jigsaw_sample.csv           # Synthetic/extended benchmark corpus (254 rows)
├── run.py                           # Single command launcher (Backend + Frontend)
├── Makefile                         # make run / test / eval / bias / build
├── docker-compose.yml               # Docker orchestration
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- Internet access on first run (for Hugging Face model download)

### 1. Install Python dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Install frontend dependencies
```bash
cd frontend
npm install
```

### 3. Download ML models (first time only - requires internet)
```bash
python ml/download_models.py
```

### 4. Launch everything with a single command
```bash
python run.py
```

This starts:
- **Backend API** at http://localhost:8000 (FastAPI, Uvicorn)
- **Frontend UI** at http://localhost:5173 (React, Vite)

---

## Running Tests

```bash
# Backend API + rewrite rule tests (12 tests)
pytest backend/tests -v

# Frontend production build smoke test
python frontend/smoke_test.py

# ML rewrite evaluation (200 test comments)
python ml/eval_rewrite.py

# Identity bias analysis
python ml/bias_check.py
```

---

## API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | Health check → `{"status": "online"}` |
| `/samples` | `GET` | 5 curated sample messages |
| `/analyze` | `POST` | Multi-label toxicity + tone analysis |
| `/rewrite` | `POST` | Semantic rewrite in chosen style mode |
| `/conversations` | `POST` | Parse and analyze a full chat thread |
| `/conversations` | `GET` | List all stored conversations |
| `/conversations/{id}` | `GET` | Get a specific conversation with messages |
| `/insights` | `GET` | Aggregate statistics across all analyses |

### Request/Response Shapes
```jsonc
// POST /analyze
{ "text": "Your code is completely wrong." }
// → { toxicity_score: 48.2, label: "Caution", tone: "Rude", categories: {...}, flagged_tokens: [...] }

// POST /rewrite
{ "text": "...", "mode": "Constructive" }  // mode: Constructive|Professional|Friendly|Neutral
// → { original: "...", rewrite: "...", new_toxicity_score: 0.1, similarity: 0.73 }
```

---

## ML Pipeline Details

### 1. Toxicity Model

**Baseline**: TF-IDF (1-2 ngrams, 5000 features) + One-vs-Rest Logistic Regression with balanced class weighting.

**Production Fallback**: `unitary/toxic-bert` — a pretrained multi-label BERT model fine-tuned on the full Jigsaw Toxic Comment Classification dataset. This is used automatically in CPU-only environments.

**DistilBERT Fine-tuning**: Available in `ml/train_distilbert.py` and `ml/train_colab.ipynb`. Requires GPU for practical training time.
> **⚠️ Training Note**: For fine-tuning DistilBERT on the full Jigsaw dataset (~159K rows, 2 epochs), **Google Colab (GPU runtime: T4 or A100)** is required. Open `ml/train_colab.ipynb` in Google Colab and follow the step-by-step notebook. Download the resulting `toxicity_model.zip` and extract it to `ml/artifacts/toxicity_model/` before running locally.

**Labels**: `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`

### 2. UI Category Mapping

The UI displays 6 category bars mapped directly from Jigsaw labels:

| UI Category | Source Label | Method |
| :--- | :--- | :--- |
| Toxic | `toxic` | Direct model probability |
| Insult | `insult` | Direct model probability |
| Harassment | Derived | `max(insult, threat) × (1.25 if 2nd-person target else 0.80)` |
| Obscene | `obscene` | Direct model probability |
| Threat | `threat` | Direct model probability |
| Identity Attack | `identity_hate` | Direct model probability |

**Harassment Heuristic**: The model detects the presence of 2nd-person targeting pronouns (`you`, `your`, `yourself`, `@mentions`) and amplifies the harassment score by ×1.25 when present (targeting implies intent to harm a specific person), or attenuates by ×0.80 for impersonal statements. The raw value is capped at 1.0 (100%).

**Overall Toxicity % = model's raw `toxic` probability** (not an average across categories).

### 3. Toxicity Classification Thresholds

| Score Range | Status Label | Interpretation |
| :--- | :--- | :--- |
| < 30% | ✅ Safe | Message appears respectful and appropriate |
| 30% – 60% | ⚠️ Caution | Potentially harsh, ambiguous, or blunt phrasing |
| > 60% | ❌ Toxic | Strongly abusive, hostile, or harmful language |

Thresholds are configurable via the `.env` file or `config.py`.

**Tone Consistency Rule** (always enforced): If the detected tone is **Rude** or **Aggressive**, the status badge will **never** show "Safe" even when toxicity score is below 30%. It automatically escalates to "Caution" with explanation: *"Not toxic (X%), but may come across as rude/aggressive."*

### 4. Tone Classifier

**Method**: Rule-based multi-pattern classifier with weighted scores, designed around Stanford Politeness Corpus patterns and GoEmotions categories.

**Supported Tones**: `Polite`, `Neutral`, `Rude`, `Aggressive`, `Sarcastic-ish/Passive-aggressive`, `Friendly`

**Choice Rationale**: Zero-shot classification via `facebook/bart-large-mnli` was evaluated but found too slow (>5s per inference) for real-time interactive use. The rule-based classifier achieves sub-millisecond classification and provides stronger interpretability.

### 5. Rewriter

**Modes**: Constructive, Professional, Friendly, Neutral

**Method**: Intent-aware semantic template rewriter that:
1. Detects the topic of the hostile message (code quality, documentation, build failure, etc.)
2. Selects the appropriate constructive template matching the topic and mode
3. Verifies the rewrite is **not identical** to the original (strict assertion)
4. Re-scores with `unitary/toxic-bert` and measures semantic similarity via `sentence-transformers/all-MiniLM-L6-v2`
5. If toxicity doesn't drop or similarity < 0.60, generates candidate 2 and returns the best

**Pluggable Architecture**: The rewriter is designed with a provider interface — you can plug in an OpenAI/Gemini API key (via env var) for LLM-powered rewrites. Without an API key, the template engine is used.

---

## Model Evaluation Metrics

### Toxicity Baseline Metrics (Jigsaw Benchmark Corpus)

| Category | ROC-AUC | F1-Score | Precision | Recall | Tuned Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **toxic** | 0.9881 | 0.9474 | 0.9310 | 0.9643 | `0.55` |
| **severe_toxic** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `0.65` |
| **obscene** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `0.30` |
| **threat** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `0.35` |
| **insult** | 0.9838 | 0.9333 | 0.9130 | 0.9545 | `0.55` |
| **identity_hate** | 1.0000 | 0.9091 | 0.8333 | 1.0000 | `0.30` |
| **MACRO AVERAGE** | **0.9953** | **0.9650** | — | — | — |

> *Metrics on 25% held-out stratified split of the synthetic benchmark corpus. Full Jigsaw training requires Colab notebook.*

### Rewrite Evaluation (200 Test Comments)

| Mode | Samples | Avg Baseline Toxicity | Avg Post-Rewrite Toxicity | Net Reduction | Mean Similarity | Verbatim Leaks |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Constructive** | 50 | 8.2% | 0.1% | **-8.1%** | 0.600 | 0 |
| **Professional** | 50 | 9.5% | 0.1% | **-9.4%** | 0.600 | 0 |
| **Friendly** | 50 | 12.4% | 0.1% | **-12.3%** | 0.600 | 0 |
| **Neutral** | 50 | 13.3% | 0.1% | **-13.2%** | 0.600 | 0 |

---

## Bias Analysis Summary

Identity bias test: 23 neutral or positive statements about protected demographic groups were run through the toxicity classifier.

| Demographic Group | False Positive Rate | Avg Toxicity |
| :--- | :--- | :--- |
| **Disability** | 0.0% | 0.40% |
| **Race & Ethnicity** | 0.0% | 0.10% |
| **Religion** | 0.0% | 0.10% |
| **Sexual Orientation & Gender Identity** | 16.7% | 5.50% |
| **General Neutral Baseline** | 0.0% | 1.30% |

**Notable Finding**: "She is a lesbian software developer working on backend APIs." scored 30.9% (marginal threshold). This reflects known bias in the Jigsaw training dataset where the word "lesbian" was disproportionately co-located with toxic content. The 30% Safe/Caution threshold prevents this from triggering action on clearly benign statements. See `ml/reports/bias.md` for full detail.

---

## Dataset Sources

| Dataset | Use | Location |
| :--- | :--- | :--- |
| Jigsaw Toxic Comment Classification | Multi-label toxicity training | [Kaggle](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge) / Synthetic benchmark at `/data/jigsaw_sample.csv` |
| unitary/toxic-bert | Production CPU inference fallback | [HuggingFace](https://huggingface.co/unitary/toxic-bert) |
| sentence-transformers/all-MiniLM-L6-v2 | Semantic similarity for rewrite scoring | [HuggingFace](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |

---

## Known Limitations

1. **CPU Inference Speed**: The `unitary/toxic-bert` model runs in ~0.5–2s per query on CPU. For production scale, use GPU inference or a quantized model (e.g., via ONNX).
2. **Short Text Reliability**: Very short messages (<5 words) may produce less reliable multi-label scores due to limited context for the BERT attention mechanism.
3. **Rewriter Templates**: The current rewriter uses a template-based engine with topic-aware branching. For nuanced domain-specific messages (medical, legal), plugging in an LLM provider (OpenAI/Gemini API key via env var) will produce significantly richer rewrites.
4. **Tone Classifier Limitations**: The rule-based classifier can miss subtle sarcasm in formally polite language or complex multi-layered passive aggression.
5. **Language Coverage**: English-only. Multi-lingual support would require a multilingual backbone (e.g., `xlm-roberta`).
6. **Bias in Training Data**: The Jigsaw dataset contains documented historical biases where identity terms appear in toxic comments at disproportionate rates. The 30% threshold and contextual BERT encoding mitigate but do not eliminate these effects.

---

## Ethical Use Notice

> **This tool is an assistive writing aid, not an automated content moderator or censorship system.**
> 
> Toxicity and tone scores are probabilistic estimates derived from statistical patterns in imperfect training data. They should be used to:
> - **Help** writers recognize unintentionally harsh phrasing before sending
> - **Suggest** alternative, more constructive framings
> - **Monitor** communication health trends in team collaboration
> 
> They should **not** be used to:
> - Automatically block, penalize, or moderate communications without human oversight
> - Make employment, legal, or disciplinary decisions
> - Determine intent or malice with certainty
> 
> Model predictions can be wrong, biased, or context-insensitive. Always apply human judgment when interpreting results.

---

## Development Guide

### Backend Development
```bash
# Hot-reload backend
uvicorn backend.app.main:app --reload --port 8000

# Interactive API docs
open http://localhost:8000/docs
```

### Frontend Development  
```bash
cd frontend
npm run dev
# Hot module replacement at http://localhost:5173
```

### Adding a New Rewrite Mode
1. Add the mode label to `RewriterEngine._transform_intent()` in `/ml/rewriter.py`
2. Update the Pydantic schema `mode` validation in `/backend/app/schemas.py`
3. Add the button to the segmented control in `/frontend/src/components/AnalyzeTab.tsx`

### Environment Variables
Copy `.env.example` → `.env`:
```env
DATABASE_URL=sqlite:///./tone_checker.db
SAFE_THRESHOLD=30.0
CAUTION_THRESHOLD=60.0
MAX_TEXT_LENGTH=1000
PORT=8000
HOST=0.0.0.0
```

