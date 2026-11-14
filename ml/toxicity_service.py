"""
Toxicity Classification Service
Wraps fine-tuned DistilBERT (from Colab training) with fallback to unitary/toxic-bert.
Priority:
  1. ml/artifacts/toxicity_model/toxicity_model  (Colab-trained DistilBERT — preferred)
  2. ml/artifacts/toxicity_model                 (direct save)
  3. unitary/toxic-bert                          (HF-cached pretrained fallback)
Provides:
  - 6 category scores (Toxic, Insult, Harassment, Obscene, Threat, Identity Attack)
  - Harassment heuristic
  - Overall toxicity %
  - Flagged tokens with attribution weights
  - Tone integration & Tone consistency rule
"""

import os
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import re
import torch
import numpy as np
from typing import Dict, List, Any, Tuple

# Ensure root dir in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from ml.tone_classifier import ToneClassifier
except ImportError:
    from tone_classifier import ToneClassifier
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Label order must match the column order used during Colab training:
# LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
JIGSAW_LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

def _resolve_model_path(default: str = "unitary/toxic-bert") -> tuple[str, str]:
    """
    Resolves model path with priority:
      1. artifacts/toxicity_model/toxicity_model  (Colab zip extracts here)
      2. artifacts/toxicity_model                 (direct save)
      3. default (unitary/toxic-bert HF cache)
    Returns (resolved_path, source_description).
    """
    artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")

    # Priority 1: nested path (Colab zip → extract → toxicity_model/toxicity_model)
    nested = os.path.join(artifacts_dir, "toxicity_model", "toxicity_model")
    if os.path.isdir(nested) and os.path.exists(os.path.join(nested, "config.json")):
        return nested, "Colab fine-tuned DistilBERT (nested)"

    # Priority 2: flat artifacts/toxicity_model
    flat = os.path.join(artifacts_dir, "toxicity_model")
    if os.path.isdir(flat) and os.path.exists(os.path.join(flat, "config.json")):
        return flat, "Colab fine-tuned DistilBERT (flat)"

    # Priority 3: HF pretrained fallback
    return default, f"pretrained fallback ({default})"


def _sanity_check_model(model, tokenizer, device: str) -> bool:
    """
    Quick sanity check: run a known-toxic sentence through the model.
    Returns True if the model is discriminative (max prob > 0.6 OR min prob < 0.4),
    False if all outputs are stuck near 0.5 (untrained classifier head).
    """
    probe = "You are an absolute idiot and a complete moron."
    inputs = tokenizer(probe, return_tensors="pt", truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits[0]
        probs = torch.sigmoid(logits).cpu().numpy()
    max_p, min_p = float(probs.max()), float(probs.min())
    spread = max_p - min_p
    is_discriminative = spread > 0.1 or max_p > 0.6
    if not is_discriminative:
        print(f"  ⚠️  Sanity check FAILED: probs={[round(float(p),3) for p in probs]} "
              f"(spread={spread:.3f}) — classifier head appears untrained.")
    else:
        print(f"  ✓  Sanity check PASSED: max_prob={max_p:.3f}, spread={spread:.3f}")
    return is_discriminative


class ToxicityService:
    def __init__(self, model_path_or_name: str = "unitary/toxic-bert"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        resolved_path, source = _resolve_model_path(model_path_or_name)
        print(f"ToxicityService loading [{source}] on {self.device}...")

        tokenizer = AutoTokenizer.from_pretrained(resolved_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(
            resolved_path, local_files_only=True
        )
        model.to(self.device)
        model.eval()

        # Sanity check: auto-fallback if classifier head is untrained (all probs ~0.5)
        if not _sanity_check_model(model, tokenizer, self.device):
            print(f"  → Falling back to unitary/toxic-bert (classifier head in '{source}' is untrained).")
            print(f"  → Tip: re-run your Colab notebook for the full 2 epochs and re-download the model.")
            fallback_path = "unitary/toxic-bert"
            tokenizer = AutoTokenizer.from_pretrained(fallback_path)
            model = AutoModelForSequenceClassification.from_pretrained(fallback_path)
            model.to(self.device)
            model.eval()
            source = f"pretrained fallback (unitary/toxic-bert) [local DistilBERT head untrained]"

        self.tokenizer = tokenizer
        self.model = model
        self._source = source

        # Determine label order from model config (supports both named and LABEL_N formats)
        id2label = self.model.config.id2label  # {0: "toxic", ...} or {0: "LABEL_0", ...}
        num_labels = len(id2label)

        # Build index→jigsaw_key mapping
        # Named: id2label[0] = "toxic" → matches JIGSAW_LABELS directly
        # Generic: id2label[0] = "LABEL_0" → use positional JIGSAW_LABELS order
        self._label_indices: Dict[str, int] = {}
        first_label = id2label.get(0, "LABEL_0")
        if first_label in JIGSAW_LABELS:
            # Named labels — map each index to its jigsaw key
            for idx, lbl in id2label.items():
                if lbl in JIGSAW_LABELS:
                    self._label_indices[lbl] = int(idx)
        else:
            # Generic LABEL_N — assume positional order matches JIGSAW_LABELS
            for i, lbl in enumerate(JIGSAW_LABELS):
                if i < num_labels:
                    self._label_indices[lbl] = i

        print(f"  Label mapping: {self._label_indices}")
        self.tone_classifier = ToneClassifier()

    def _detect_flagged_tokens(self, text: str, base_toxic_prob: float, detected_tone: str = "Neutral") -> List[Dict[str, Any]]:
        """
        Calculates token attribution using lightweight occlusion or lexicon matching.
        Returns a list of {token: str, weight: float}.
        """
        words = re.findall(r"[\w']+|[.,!?;]", text)
        is_harsh_tone = detected_tone in ["Rude", "Aggressive", "Sarcastic-ish/Passive-aggressive"]
        if not words or (base_toxic_prob < 0.05 and not is_harsh_tone):
            return []

        # High priority words known to heavily impact toxicity
        flagged = []
        clean_words = [w.lower() for w in words if len(w) > 1 and w.isalpha()]
        
        # Word-level occlusion for words in the sentence
        if base_toxic_prob >= 0.25 and len(clean_words) <= 30:
            for w in set(clean_words):
                # Pattern to replace word with mask or empty
                occluded_text = re.sub(rf"\b{re.escape(w)}\b", "", text, flags=re.IGNORECASE).strip()
                if not occluded_text:
                    continue
                inputs = self.tokenizer(occluded_text, return_tensors="pt", truncation=True, max_length=128).to(self.device)
                with torch.no_grad():
                    logits = self.model(**inputs).logits
                    probs = torch.sigmoid(logits)[0].cpu().numpy()
                    toxic_idx = self._label_indices.get("toxic", 0)
                    drop = base_toxic_prob - float(probs[toxic_idx])
                    if drop > 0.05:
                        weight = min(1.0, round(drop / max(base_toxic_prob, 0.01) * 1.5, 3))
                        flagged.append({"token": w, "weight": max(0.1, weight)})

        # Fallback to toxic keywords and harsh/dismissive workplace terms
        if not flagged:
            toxic_lexicon = {
                "fuck": 0.95, "fucking": 0.95, "shit": 0.85, "idiot": 0.80, "moron": 0.82,
                "bitch": 0.92, "asshole": 0.90, "kill": 0.90, "destroy": 0.65, "clown": 0.55,
                "loser": 0.60, "stupid": 0.70, "hate": 0.65, "crap": 0.50, "garbage": 0.65,
                "threat": 0.80, "incompetent": 0.65, "disgusting": 0.75, "freak": 0.78,
                "unacceptable": 0.65, "subpar": 0.55, "sloppy": 0.50, "shoddy": 0.60,
                "terrible": 0.60, "useless": 0.70, "ridiculous": 0.55, "pathetic": 0.70,
                "clueless": 0.60, "atrocious": 0.70, "abysmal": 0.70, "disaster": 0.60
            }
            for w in clean_words:
                if w in toxic_lexicon:
                    if base_toxic_prob > 0.15 or is_harsh_tone:
                        flagged.append({"token": w, "weight": toxic_lexicon[w]})

        # Deduplicate and sort descending by weight
        seen = set()
        deduped = []
        for item in sorted(flagged, key=lambda x: x["weight"], reverse=True):
            if item["token"].lower() not in seen:
                seen.add(item["token"].lower())
                deduped.append(item)
        return deduped[:8]

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Runs comprehensive analysis:
        Returns:
          - toxicity_score: float (percentage 0 - 100)
          - label: "Safe" | "Caution" | "Toxic"
          - tone: str
          - categories: {toxic, insult, harassment, obscene, threat, identity_attack}
          - char_count: int
          - flagged_tokens: [{token, weight}]
          - explanation: str
        """
        text_clean = text.strip()
        if not text_clean:
            return {
                "toxicity_score": 0.0,
                "label": "Safe",
                "tone": "Neutral",
                "categories": {
                    "toxic": 0.0,
                    "insult": 0.0,
                    "harassment": 0.0,
                    "obscene": 0.0,
                    "threat": 0.0,
                    "identity_attack": 0.0
                },
                "char_count": 0,
                "flagged_tokens": [],
                "explanation": "No text provided."
            }

        inputs = self.tokenizer(text_clean, return_tensors="pt", truncation=True, max_length=128).to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            raw_probs = torch.sigmoid(logits)[0].cpu().numpy()

        # Map output indices → Jigsaw label keys using the resolved label mapping
        prob_dict = {}
        for label_key, idx in self._label_indices.items():
            prob_dict[label_key] = float(raw_probs[idx]) if idx < len(raw_probs) else 0.0
        # Ensure all keys exist
        for lbl in JIGSAW_LABELS:
            if lbl not in prob_dict:
                prob_dict[lbl] = 0.0

        # Harassment heuristic:
        # max(insult, threat) weighted by whether the message targets 2nd person (you, your, names/@mentions)
        has_second_person = bool(re.search(r"\b(you|your|you're|yours|yourself|u|ur|@\w+)\b", text_clean, re.IGNORECASE))
        multiplier = 1.25 if has_second_person else 0.8
        harassment_raw = min(1.0, max(prob_dict["insult"], prob_dict["threat"]) * multiplier)

        # Build UI category scores (0 - 100%)
        categories = {
            "toxic": round(prob_dict["toxic"] * 100.0, 1),
            "insult": round(prob_dict["insult"] * 100.0, 1),
            "harassment": round(harassment_raw * 100.0, 1),
            "obscene": round(prob_dict["obscene"] * 100.0, 1),
            "threat": round(prob_dict["threat"] * 100.0, 1),
            "identity_attack": round(prob_dict["identity_hate"] * 100.0, 1),
        }

        # Overall toxicity % is the model's "toxic" probability
        overall_toxicity_pct = round(prob_dict["toxic"] * 100.0, 1)

        # Tone detection
        detected_tone, tone_scores, tone_exp = self.tone_classifier.predict(text_clean, prob_dict)

        # Baseline Label determination (<30% Safe, 30-60% Caution, >60% Toxic)
        if overall_toxicity_pct < 30.0:
            status_label = "Safe"
            explanation = "Your message appears respectful and safe to send."
        elif overall_toxicity_pct <= 60.0:
            status_label = "Caution"
            explanation = "Contains potentially sensitive, harsh, or ambiguous phrasing."
        else:
            status_label = "Toxic"
            explanation = "Contains strongly toxic, hostile, or abusive language."

        # Tone Consistency Rule:
        # If detected tone is Rude, Aggressive, or Sarcastic/Passive-aggressive,
        # status badge MUST NEVER say "Safe" even when toxicity score is low (<30%);
        # use "Caution" with a note like "Not toxic, but may come across as rude".
        if detected_tone in ["Rude", "Aggressive", "Sarcastic-ish/Passive-aggressive"] and status_label == "Safe":
            status_label = "Caution"
            explanation = f"Not toxic ({overall_toxicity_pct}%), but may come across as {detected_tone.lower()}."

        # Flagged tokens
        flagged_tokens = self._detect_flagged_tokens(text_clean, prob_dict["toxic"], detected_tone)

        return {
            "toxicity_score": overall_toxicity_pct,
            "label": status_label,
            "tone": detected_tone,
            "tone_scores": tone_scores,
            "categories": categories,
            "char_count": len(text_clean),
            "flagged_tokens": flagged_tokens,
            "explanation": explanation
        }

if __name__ == "__main__":
    service = ToxicityService()
    samples = [
        "Please review the PR when you get a chance.",
        "Did you even bother reading the ticket before coding this?",
        "You are an absolute idiot and a complete moron.",
        "I will kill you if you do that again.",
        "I am a gay man living in California and I love open-source software."
    ]
    for s in samples:
        res = service.analyze(s)
        print(f"Text: '{s}'")
        print(f" -> Score: {res['toxicity_score']}% | Label: {res['label']} | Tone: {res['tone']}")
        print(f" -> Categories: {res['categories']}")
        print(f" -> Flagged: {res['flagged_tokens']}")
        print(f" -> Explanation: {res['explanation']}\n")
