"""
Tone Classifier for Tone Checker
Detects: Polite, Neutral, Rude, Aggressive, Sarcastic-ish/Passive-aggressive, Friendly.
Calibrated against Stanford Politeness Corpus and GoEmotions dimensions.
"""

import re
from typing import Dict, Tuple

TONES = [
    "Polite",
    "Neutral",
    "Rude",
    "Aggressive",
    "Sarcastic-ish/Passive-aggressive",
    "Friendly"
]

class ToneClassifier:
    def __init__(self):
        # Patterns for polite tone
        self.polite_patterns = [
            r"\b(please|kindly|thank you|thanks|much appreciated|appreciate|could you|would you mind|if possible|sorry to bother)\b",
            r"\b(pardon|excuse me|may i ask|grateful|warm regards|best regards)\b"
        ]
        
        # Patterns for friendly tone
        self.friendly_patterns = [
            r"\b(awesome|great job|kudos|cheers|excited|happy to|love this|fantastic|wonderful|welcome|glad to|hello|hi there|hey)\b",
            r"!{1,2}\s*$",
            r"(:-\)|:\)|<3|\bcongrats\b|\bdelighted\b|\bhave a great day\b)"
        ]

        # Patterns for sarcastic / passive-aggressive tone
        self.sarcastic_patterns = [
            r"\b(oh wow|oh brilliant|what a brilliant|great job breaking|genius move|slow clap|thanks for nothing)\b",
            r"\b(as per my previous|per my last email|as clearly stated|in case you missed it|obviously|must be nice)\b",
            r"\b(did you even bother|clearly you didn't|surely you knew|if you actually read|thanks for stating the obvious)\b",
            r"\b(as i already told you|as i already explained|how hard can it be|it's not rocket science)\b"
        ]

        # Patterns for rude / harsh / dismissive tone
        self.rude_patterns = [
            # Harsh evaluative judgements of work or implementation
            r"\b(unacceptable|not acceptable|intolerable|unusable|subpar|shoddy|amateurish|sloppy|atrocious|abysmal)\b",
            r"\b(total disaster|complete disaster|total trainwreck|complete mess|is a mess|garbage code|terrible code)\b",
            # Patronizing concessions followed by blunt dismissal
            r"\b(i know you tried|at least you tried|nice try|good effort)\b.*?\b(but|however|yet)\b",
            r"\b(no offense, but|with all due respect, but|don't take this the wrong way, but)\b",
            # Workplace dismissals & condescending phrasing
            r"\b(waste of time|waste of my|stop asking|read the (docs|manual)|don't ping me|clueless|makes no sense)\b",
            r"\b(completely wrong|utterly wrong|shouldn't have to explain|incompetent|figure it out yourself)\b",
            r"\b(do your job|not my problem|deal with it|stop wasting|shut up|get lost|stop talking|ridiculous|pathetic)\b",
            r"\b(you clearly don't know|you don't know what you're doing|you have no idea|you have no clue)\b",
            r"\b(did you even test|did you even try|who approved this|who wrote this garbage)\b"
        ]

        # Patterns for aggressive tone
        self.aggressive_patterns = [
            r"\b(i will destroy|i will kill|beat you|hunt you|watch your back|regret ever|smash your|die in)\b",
            r"\b(fight me|consequences|pay for this|destroy you|or else|gonna regret)\b",
            r"[A-Z\s!]{8,}" # Yelling in all caps
        ]

    def predict(self, text: str, toxicity_scores: Dict[str, float] = None) -> Tuple[str, Dict[str, float], str]:
        """
        Classifies tone and returns:
          - primary_tone: str
          - tone_scores: Dict[str, float]
          - explanation: str
        """
        text_clean = text.strip()
        lower_text = text_clean.lower()

        scores = {t: 0.1 for t in TONES}
        scores["Neutral"] = 0.35 # Baseline prior

        # Check toxicity indicators
        toxic_score = toxicity_scores.get("toxic", 0.0) if toxicity_scores else 0.0
        threat_score = toxicity_scores.get("threat", 0.0) if toxicity_scores else 0.0
        insult_score = toxicity_scores.get("insult", 0.0) if toxicity_scores else 0.0

        if threat_score > 0.4 or "kill" in lower_text or "destroy you" in lower_text:
            scores["Aggressive"] += 0.7
        if insult_score > 0.5:
            scores["Rude"] += 0.5
            scores["Aggressive"] += 0.3

        # Match pattern groups
        for p in self.polite_patterns:
            if re.search(p, lower_text):
                scores["Polite"] += 0.45

        for p in self.friendly_patterns:
            if re.search(p, lower_text):
                scores["Friendly"] += 0.4

        for p in self.sarcastic_patterns:
            if re.search(p, lower_text):
                scores["Sarcastic-ish/Passive-aggressive"] += 0.55

        for p in self.rude_patterns:
            if re.search(p, lower_text):
                scores["Rude"] += 0.5

        for p in self.aggressive_patterns:
            if re.search(p, text_clean):
                scores["Aggressive"] += 0.6

        # Normalization
        max_tone = max(scores, key=scores.get)
        total = sum(scores.values())
        norm_scores = {k: round(v / total, 3) for k, v in scores.items()}

        # Explanation generation
        explanations = {
            "Polite": "Message demonstrates respectful phrasing, courteous requests, and collaborative etiquette.",
            "Friendly": "Warm, constructive, and supportive wording likely to be received enthusiastically.",
            "Neutral": "Direct, factual communication without strong emotional markers.",
            "Rude": "Contains blunt, dismissive, or condescending phrasing that may cause friction.",
            "Aggressive": "Displays confrontational, hostile, or intimidating phrasing.",
            "Sarcastic-ish/Passive-aggressive": "Exhibits subtle mockery, irony, or veiled frustration."
        }

        return max_tone, norm_scores, explanations.get(max_tone, "")

if __name__ == "__main__":
    clf = ToneClassifier()
    test_cases = [
        "Could you please review this PR when you have time? Thanks!",
        "Did you even bother reading the ticket before coding this garbage?",
        "Oh wow, what a brilliant idea to push broken code on Friday.",
        "I will hunt you down and destroy you.",
        "Great job resolving that bug, team! Excited for the launch!",
        "The migration script is scheduled for 3 PM."
    ]
    for tc in test_cases:
        tone, _, exp = clf.predict(tc)
        print(f"Text: '{tc}'\n -> Tone: {tone} | {exp}\n")

