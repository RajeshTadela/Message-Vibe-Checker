import pytest
from ml.rewriter import RewriterEngine
from ml.toxicity_service import ToxicityService

@pytest.fixture(scope="module")
def rewriter():
    return RewriterEngine()

@pytest.fixture(scope="module")
def tox_service():
    return ToxicityService()

def test_rewrite_never_contains_original_verbatim(rewriter):
    """
    CRITICAL UNIT TEST (as requested in spec):
    The rewrite MUST preserve the original meaning and actual content and rephrase it.
    Never just prepend a phrase like 'Here is a constructive perspective:' to the original text.
    Fails if the rewrite contains the original sentence verbatim.
    """
    test_sentences = [
        "Your code is completely wrong and makes no sense at all.",
        "Did you even bother reading the ticket description before coding this?",
        "Oh wow, what a brilliant idea to break production on a Friday.",
        "Stop asking basic questions and read the documentation first.",
        "You are an absolute idiot and a complete moron who shouldn't be writing code.",
        "This entire feature is a total waste of my afternoon, fix this right now."
    ]

    forbidden_prefixes = [
        "here is a constructive perspective:",
        "constructive perspective:",
        "here is a rewrite:",
        "here is a polite version:"
    ]

    for sentence in test_sentences:
        for mode in ["Constructive", "Professional", "Friendly", "Neutral"]:
            res = rewriter.rewrite(sentence, mode=mode)
            rewritten_text = res["rewrite"]

            # 1. Must not match original sentence
            assert rewritten_text.strip().lower() != sentence.strip().lower(), (
                f"Mode {mode}: Rewrite was identical to original: '{sentence}'"
            )

            # 2. Must not contain the full original sentence as a verbatim substring
            assert sentence.strip().lower() not in rewritten_text.strip().lower(), (
                f"Mode {mode}: Rewrite contained the original sentence verbatim: '{sentence}'"
            )

            # 3. Must not simply prepend a canned prompt prefix
            for prefix in forbidden_prefixes:
                assert not rewritten_text.lower().startswith(prefix), (
                    f"Mode {mode}: Rewrite used prohibited prefix '{prefix}': {rewritten_text}"
                )

def test_semantic_similarity_floor(rewriter):
    """Verifies that meaning is preserved with sentence-transformers similarity >= 0.60."""
    test_cases = [
        "Your code is completely wrong and makes no sense at all.",
        "Did you even bother reading the ticket description before coding this?",
        "Stop asking basic questions and read the documentation first."
    ]
    for sentence in test_cases:
        for mode in ["Constructive", "Professional", "Friendly", "Neutral"]:
            res = rewriter.rewrite(sentence, mode=mode)
            assert res["similarity"] >= 0.60, (
                f"Mode {mode} semantic similarity {res['similarity']} is below 0.60 floor."
            )

def test_toxicity_reduction_loop(rewriter, tox_service):
    """Verifies that the rewriter's output has lower toxicity than the toxic input."""
    toxic_input = "You are an absolute idiot and a complete moron who shouldn't be writing code."
    scorer = lambda txt: tox_service.analyze(txt)["toxicity_score"] / 100.0

    orig_tox = tox_service.analyze(toxic_input)["toxicity_score"]
    assert orig_tox > 60.0, "Input text should be toxic"

    for mode in ["Constructive", "Professional", "Friendly", "Neutral"]:
        res = rewriter.rewrite(toxic_input, mode=mode, toxicity_scorer=scorer)
        new_tox = tox_service.analyze(res["rewrite"])["toxicity_score"]
        assert new_tox < orig_tox, f"Mode {mode} did not reduce toxicity (was {orig_tox}%, now {new_tox}%)"
        assert new_tox < 25.0, f"Mode {mode} rewritten text still has high toxicity: {new_tox}%"

