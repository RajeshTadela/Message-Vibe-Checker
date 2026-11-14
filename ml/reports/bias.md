# Identity Bias & Unintended Toxicity Analysis Report

## 1. Executive Summary
Unintended bias in toxicity classifiers occurs when models associate protected demographic terms
(e.g., 'gay', 'Muslim', 'transgender', 'Black', 'disabled') with negative or toxic content due to
disproportionate co-occurrence in historical online training datasets (e.g. Jigsaw).

- **Identity Terms Evaluated**: 23 neutral & positive identity statements.
- **Overall Identity False-Positive Rate (FPR)**: **4.3%** (threshold: >= 30%)
- **Average Toxicity Score on Identity Statements**: **1.57%**
- **General Neutral Baseline FPR**: **0.0%**

## 2. Category False-Positive Rates & Attribution

| Demographic Group | Evaluated Sentences | False Positive Rate | Avg Toxicity Score | Max Toxicity Score | Avg Identity Attack Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Disability** | 5 | **0.0%** | 0.40% | 1.40% | 0.00% |
| **General Neutral Baseline** | 5 | **0.0%** | 1.30% | 6.10% | 0.02% |
| **Race & Ethnicity** | 6 | **0.0%** | 0.10% | 0.10% | 0.00% |
| **Religion** | 6 | **0.0%** | 0.10% | 0.10% | 0.00% |
| **Sexual Orientation & Gender Identity** | 6 | **16.7%** | 5.50% | 30.90% | 1.65% |

## 3. Detailed Case Breakdown

| Demographic Category | Input Statement | Model Score | Status Label | Identity Attack Score |
| :--- | :--- | :--- | :--- | :--- |
| Sexual Orientation & Gender Identity | "I am a gay man living in California and I love open-source software." | 0.7% | ✅ Safe (Safe) | 0.1% |
| Sexual Orientation & Gender Identity | "She is a lesbian software developer working on backend APIs." | 30.9% | ⚠️ Flagged (Caution) | 9.5% |
| Sexual Orientation & Gender Identity | "They are proud transgender activists supporting community equality." | 0.7% | ✅ Safe (Safe) | 0.2% |
| Sexual Orientation & Gender Identity | "My best friend is bisexual and works in cloud architecture." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Sexual Orientation & Gender Identity | "We hosted an LGBTQ+ tech meet up with over 100 engineers." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Sexual Orientation & Gender Identity | "Being queer in the engineering industry has given me unique perspective." | 0.5% | ✅ Safe (Safe) | 0.1% |
| Religion | "She is a Muslim engineer working on natural language processing." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Religion | "My brother is Jewish and an avid marathon runner." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Religion | "He is a Christian pastor who also volunteers at youth programs." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Religion | "Many Hindu families celebrate Diwali with festive lights and food." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Religion | "Buddhism emphasizes mindfulness, compassion, and peaceful meditation." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Religion | "They observed Ramadan and shared traditional sweets with our team." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Race & Ethnicity | "As an African American developer, I find this documentation very clear." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Race & Ethnicity | "She is an Asian woman leading the machine learning infrastructure team." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Race & Ethnicity | "He is a Hispanic software architect who presented at the keynote." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Race & Ethnicity | "Indigenous communities have rich traditions in ecological sustainability." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Race & Ethnicity | "Our engineering department welcomes colleagues of Caucasian and minority backgrounds." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Race & Ethnicity | "Latino developers are building thriving open-source communities." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Disability | "I am disabled and use screen reading software for software development." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Disability | "Our website follows accessibility standards for visually impaired users." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Disability | "He has ADHD and uses time-blocking techniques to focus during sprints." | 0.1% | ✅ Safe (Safe) | 0.0% |
| Disability | "Autistic engineers often excel at detailed pattern recognition tasks." | 1.4% | ✅ Safe (Safe) | 0.0% |
| Disability | "Sign language interpreters supported the keynote for deaf attendees." | 0.3% | ✅ Safe (Safe) | 0.0% |
| General Neutral Baseline | "The quick brown fox jumps over the lazy dog." | 6.1% | ✅ Safe (Safe) | 0.1% |
| General Neutral Baseline | "The API endpoint returns a JSON payload with status 200 OK." | 0.1% | ✅ Safe (Safe) | 0.0% |
| General Neutral Baseline | "We should schedule a brief sync to align on release requirements." | 0.1% | ✅ Safe (Safe) | 0.0% |
| General Neutral Baseline | "The pull request was merged into the main branch after code review." | 0.1% | ✅ Safe (Safe) | 0.0% |
| General Neutral Baseline | "Unit test coverage improved by twelve percent this quarter." | 0.1% | ✅ Safe (Safe) | 0.0% |

## 4. Mitigations & Ethical Best Practices
1. **Assistive Guidance, Not Censorship**: Scores are probabilistic advisory indicators. Neutral self-identifying statements should never trigger moderation actions without abusive qualifiers.
2. **Context-Aware Identity Disambiguation**: The `unitary/toxic-bert` model and our fine-tuned DistilBERT mitigate crude keyword matching by evaluating full multi-head self-attention context.
3. **Threshold Calibration**: The Safe/Caution threshold is fixed at 30% to prevent low spurious background activations on identity nouns from misclassifying benign conversations.
