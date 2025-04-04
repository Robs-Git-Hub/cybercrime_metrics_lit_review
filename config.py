#config.py

import os
from pathlib import Path

class NotebookConfig:
    BASE_DIR = Path(".")
    INPUT_DIR = BASE_DIR / "input_docs"
    OUTPUT_DIR = BASE_DIR / "output_docs"
    DB_FILE = BASE_DIR / 'cybercrime_analysis.db'