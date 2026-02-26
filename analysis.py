from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


REQUIRED_COLS = ["email_id", "received_at", "sender", "subject", "body"]


def validate_input_df(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Expected: {REQUIRED_COLS}")
    out = df.copy()
    for c in REQUIRED_COLS:
        out[c] = out[c].astype(str)
    return out


def build_insights_df(df: pd.DataFrame, insights_list: list[dict]) -> pd.DataFrame:
    insights_df = pd.DataFrame(insights_list)
    return pd.concat([df.reset_index(drop=True), insights_df.reset_index(drop=True)], axis=1)


def kpi_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return (
        df[col]
        .fillna("unknown")
        .value_counts()
        .rename_axis(col)
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def top_action_items(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    # explode list-like action items
    tmp = df.copy()
    tmp["action_items"] = tmp["action_items"].apply(lambda x: x if isinstance(x, list) else [])
    exploded = tmp.explode("action_items")
    exploded["action_items"] = exploded["action_items"].astype(str).str.strip()
    exploded = exploded[exploded["action_items"].ne("") & exploded["action_items"].ne("[]")]
    return (
        exploded["action_items"]
        .value_counts()
        .head(n)
        .rename_axis("action_item")
        .reset_index(name="count")
    )