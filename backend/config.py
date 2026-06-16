import os
from pathlib import Path

BACKEND_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = BACKEND_DIR.parent

DATA_DIR = os.environ.get("AISTUDIO_DATA_DIR", str(PROJECT_DIR / "data"))
MODELS_DIR = os.environ.get("AISTUDIO_MODELS_DIR", str(Path(DATA_DIR) / "models"))
DB_PATH = os.environ.get("AISTUDIO_DB_PATH", str(Path(DATA_DIR) / "aistudio.db"))
HF_CACHE_DIR = os.environ.get("AISTUDIO_HF_CACHE", str(Path(DATA_DIR) / "hf_cache"))

TRAINING_SCRIPT = str(BACKEND_DIR / "scripts" / "train_lora.py")
EVAL_SCRIPT = str(BACKEND_DIR / "scripts" / "evaluate.py")
API_SERVER_SCRIPT = str(BACKEND_DIR / "scripts" / "api_server.py")

API_HOST = os.environ.get("AISTUDIO_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("AISTUDIO_PORT", "8000"))

DEFAULT_EPOCHS = 3
DEFAULT_BATCH_SIZE = 4
DEFAULT_LEARNING_RATE = 2e-4
DEFAULT_LORA_R = 8
DEFAULT_LORA_ALPHA = 32
DEFAULT_MAX_LENGTH = 512
