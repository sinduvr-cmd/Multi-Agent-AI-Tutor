"""
Loader for verified demo questions.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

JSON_PATH = Path(__file__).resolve().parent / "demo_questions.json"


def get_verified_demo_questions() -> List[Dict[str, Any]]:
    if not JSON_PATH.exists():
        return []
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
