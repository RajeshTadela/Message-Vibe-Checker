"""Manual verification script for all ML components."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

from ml.toxicity_service import ToxicityService
from ml.rewriter import RewriterEngine as Rewriter

print("=" * 60)
print("TOXICITY SERVICE VERIFICATION")
print("=" * 60)

svc = ToxicityService()

tests = [
    ('Could you please review the pull request when you have a moment?', 'Safe', 'Polite'),
    ('Stop asking basic questions and read the documentation first.', 'Caution', 'Rude'),
    ('You are an absolute idiot and a complete moron.', 'Toxic', 'Rude'),
    ('I will find where you live and destroy you.', 'Toxic', 'Aggressive'),
    ('All immigrants are subhuman scum.', 'Toxic', None),
]

all_pass = True
for text, exp_label, exp_tone in tests:
    r = svc.analyze(text)
    ok_label = r['label'] == exp_label
    ok_tone = exp_tone is None or r['tone'] == exp_tone
    status = 'PASS' if (ok_label and ok_tone) else 'FAIL'
    if status == 'FAIL':
        all_pass = False
    tone_disp = r['tone'] + ('==' if ok_tone else '!=' + str(exp_tone))
    label_disp = r['label'] + ('==' if ok_label else '!=' + exp_label)
    print(f"  [{status}] label={label_disp}, tone={tone_disp}, score={r['toxicity_score']:.1f}%")
    print(f"        text: {text[:55]}...")

print()
print("Toxicity service overall:", "ALL PASS ✓" if all_pass else "SOME FAILURES ✗")

print()
print("=" * 60)
print("TONE CONSISTENCY RULE CHECK")
print("=" * 60)
rude_text = "Stop asking basic questions and read the documentation first."
r = svc.analyze(rude_text)
tone_rule_ok = r['tone'] in ('Rude', 'Aggressive') and r['label'] != 'Safe'
print(f"  Rude text -> tone={r['tone']}, label={r['label']}")
print(f"  Tone consistency rule: {'PASS ✓' if tone_rule_ok else 'FAIL ✗'}")

print()
print("=" * 60)
print("REWRITER VERIFICATION - ALL 4 MODES")
print("=" * 60)
rw = Rewriter()
toxic = 'You are an absolute idiot and a complete moron who should not be writing code.'
modes = ['Constructive', 'Professional', 'Friendly', 'Neutral']
rw_all_pass = True
for mode in modes:
    r = rw.rewrite(toxic, mode)
    verbatim = toxic.strip().lower() in r['rewrite'].strip().lower()
    sim_ok = r['similarity'] >= 0.6
    tox_drop = r['new_toxicity_score'] < 50
    ok = not verbatim and sim_ok and tox_drop
    if not ok:
        rw_all_pass = False
    status = 'PASS' if ok else 'FAIL'
    print(f"  [{status}] mode={mode}: verbatim={verbatim}, sim={r['similarity']:.2f}, newtox={r['new_toxicity_score']:.1f}%")
    print(f"        rewrite: {r['rewrite'][:70]}...")

print()
print("Rewriter overall:", "ALL PASS ✓" if rw_all_pass else "SOME FAILURES ✗")

print()
print("=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)
overall = all_pass and rw_all_pass and tone_rule_ok
print(f"  Toxicity service:      {'✓ PASS' if all_pass else '✗ FAIL'}")
print(f"  Tone consistency rule: {'✓ PASS' if tone_rule_ok else '✗ FAIL'}")
print(f"  Rewriter (all modes):  {'✓ PASS' if rw_all_pass else '✗ FAIL'}")
print()
print(f"  OVERALL: {'ALL SYSTEMS NOMINAL ✓' if overall else 'FAILURES DETECTED ✗'}")
