# Toxicity Classification Metrics & Model Report

## 1. Overview
This report details the evaluation metrics for the Toxicity Classification system across all 6 core Jigsaw categories:
`toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, and `identity_hate`.

### Model Architecture
- **Baseline**: TF-IDF (1-2 ngrams, sublinear term frequency, English stop words) + One-vs-Rest Logistic Regression with balanced class weighting.
- **Deep Learning (Fine-Tuning)**: DistilBERT (`distilbert-base-uncased`), 128 max sequence length, 2 epochs, multi-label BCEWithLogitsLoss with class weights (implemented in `/ml/train_distilbert.py` & `/ml/train_colab.ipynb`).
- **Production Inference**: Fallback support to pretrained `unitary/toxic-bert` (fine-tuned multi-label BERT on Jigsaw) for zero-latency local CPU inference or local saved artifacts.

## 2. Evaluation Metrics (Validation Split)

| Category | ROC-AUC | F1-Score | Precision | Recall | Tuned Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **toxic** | 0.9881 | 0.9474 | 0.9310 | 0.9643 | `0.55` |
| **severe_toxic** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `0.65` |
| **obscene** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `0.3` |
| **threat** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `0.35` |
| **insult** | 0.9838 | 0.9333 | 0.9130 | 0.9545 | `0.55` |
| **identity_hate** | 1.0000 | 0.9091 | 0.8333 | 1.0000 | `0.3` |
| **MACRO AVERAGE** | **0.9953** | **0.9650** | - | - | - |

## 3. Threshold Calibration Notes
- Optimal thresholds were determined via grid search over precision-recall curves maximizing the F1 score per category.
- For UI display, raw model sigmoid probabilities are mapped directly into percentages [0-100%].
- The derived **Harassment** score uses a contextual heuristic combining `max(insult, threat)` with a 2nd-person pronoun amplifier (`you`, `your`, `@name`).
