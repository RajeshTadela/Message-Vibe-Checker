"""
Utility to download and cache required Hugging Face models:
1. sentence-transformers/all-MiniLM-L6-v2 (for semantic similarity)
2. unitary/toxic-bert (for multi-label toxicity inference)
"""

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def download_all():
    print("Downloading all-MiniLM-L6-v2...")
    SentenceTransformer("all-MiniLM-L6-v2")
    print("all-MiniLM-L6-v2 ready!")

    print("Downloading unitary/toxic-bert...")
    AutoTokenizer.from_pretrained("unitary/toxic-bert")
    AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
    print("unitary/toxic-bert ready!")

if __name__ == "__main__":
    download_all()

