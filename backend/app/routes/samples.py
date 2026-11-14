from fastapi import APIRouter
from typing import List
from backend.app.schemas import SampleItem

router = APIRouter(tags=["Samples"])

SAMPLE_MESSAGES = [
    SampleItem(
        id="sample-1",
        title="Sample 1: Safe & Polite",
        category="Safe",
        text="Could you please review the pull request when you have a moment? Thanks for your help!",
        expected_tone="Polite",
        expected_label="Safe"
    ),
    SampleItem(
        id="sample-2",
        title="Sample 2: Rude (Non-Toxic)",
        category="Rude",
        text="Stop asking basic questions and read the documentation first.",
        expected_tone="Rude",
        expected_label="Caution"
    ),
    SampleItem(
        id="sample-3",
        title="Sample 3: Direct Insult",
        category="Insult",
        text="You are an absolute idiot and a complete moron who shouldn't be writing code.",
        expected_tone="Rude",
        expected_label="Toxic"
    ),
    SampleItem(
        id="sample-4",
        title="Sample 4: Violent Threat",
        category="Threat",
        text="I will find where you live and destroy you if you touch that database again.",
        expected_tone="Aggressive",
        expected_label="Toxic"
    ),
    SampleItem(
        id="sample-5",
        title="Sample 5: Identity Attack",
        category="Identity Attack",
        text="All immigrants are subhuman scum who should be kicked out immediately.",
        expected_tone="Aggressive",
        expected_label="Toxic"
    ),
]

@router.get("/samples", response_model=List[SampleItem])
def get_samples():
    """Returns 5 curated sample messages demonstrating different toxicity categories and tones."""
    return SAMPLE_MESSAGES

