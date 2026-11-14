import os
import sys

# Set offline environment variables
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Ensure root in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ml.toxicity_service import ToxicityService
from ml.rewriter import RewriterEngine

class MLContainer:
    _instance = None

    def __init__(self):
        print("Initializing ML models inside MLContainer...")
        self.toxicity_service = ToxicityService()
        self.rewriter_engine = RewriterEngine()
        print("MLContainer loaded successfully!")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MLContainer()
        return cls._instance

def get_ml() -> MLContainer:
    return MLContainer.get_instance()

