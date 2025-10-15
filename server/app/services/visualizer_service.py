from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from .db import fetch_collection


def get_visualization_payload(source: Optional[str] = None) -> Dict[str, Any]:
    """Aggregate polarity by date and compute top keywords from stored polarity data.

    Args:
        source: Optional source filter

    Returns:
        Dict payload with trends and summary series.
    """
    records = fetch_collection("PolarityData")
    if source:
        records = [r for r in records if r.get("source") == source]

    if not records:
        return {"trends": [], "summary": {}}

    df = pd.DataFrame(records)
    if "pub_date" in df.columns:
        df["pub_date"] = pd.to_datetime(df["pub_date"])  # mongo datetime
        df["date"] = df["pub_date"].dt.date
    else:
        df["date"] = None

    grouped = (
        df.groupby("date")["compound"].mean().reset_index().rename(columns={"compound": "avg_compound"})
    )

    trends = [{"date": str(r["date"]), "avg_compound": float(r["avg_compound"]) } for _, r in grouped.iterrows()]

    summary = {
        "count": int(len(df)),
        "avg_compound": float(df.get("compound", pd.Series([0])).mean()) if "compound" in df else 0.0,
        "pos": int((df.get("label", pd.Series([])) == 1).sum()) if "label" in df else 0,
        "neg": int((df.get("label", pd.Series([])) == -1).sum()) if "label" in df else 0,
        "neu": int((df.get("label", pd.Series([])) == 0).sum()) if "label" in df else 0,
    }

    return {"trends": trends, "summary": summary}
