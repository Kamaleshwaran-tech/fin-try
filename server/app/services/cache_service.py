from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, Dict, Any

import pandas as pd

from ..core.config import get_settings


def append_mean_polarity_csv(results: Iterable[Dict[str, Any]]) -> str:
    """Append daily mean polarity to a CSV cache.

    Returns the CSV path written.
    """
    settings = get_settings()
    csv_path = settings.cache_csv_path
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    rows = list(results)
    if not rows:
        return csv_path

    compounds = [float(r.get("scores", {}).get("compound", 0.0)) for r in rows]
    labels = [int(r.get("label", 0)) for r in rows]

    today = datetime.utcnow().date()
    entry = {
        "date": str(today),
        "mean_compound": float(sum(compounds) / max(len(compounds), 1)),
        "count": len(compounds),
        "pos": int(sum(1 for l in labels if l == 1)),
        "neg": int(sum(1 for l in labels if l == -1)),
        "neu": int(sum(1 for l in labels if l == 0)),
    }

    df_new = pd.DataFrame([entry])

    if os.path.isfile(csv_path):
        df_old = pd.read_csv(csv_path)
        # Drop any existing row for today to avoid duplicates
        df_old = df_old[df_old["date"] != entry["date"]]
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(csv_path, index=False)
    return csv_path
