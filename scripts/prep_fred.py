"""Fetch and cache the FRED macro series used in Lecture 2 (VAR / Granger causality).

Run once:  python scripts/prep_fred.py
Writes:    data/processed/fred_monthly.csv

Why cache rather than call FRED live in the lab: an in-class exercise must not depend
on the network or on a FRED API key. These three series are downloaded from FRED's
public CSV endpoint (no key required) and written to disk; the lab reads the CSV.

Series
------
UNRATE  Unemployment Rate (%, monthly, seasonally adjusted)
UMCSENT University of Michigan: Consumer Sentiment (index 1966:Q1=100, monthly)
RSXFS   Retail Sales: Retail Trade and Food Services (millions of $, monthly, SA)

RSXFS begins 1992-01, which sets the joined sample.
"""
from __future__ import annotations
import io
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

SERIES = ["UNRATE", "UMCSENT", "RSXFS"]
OUT = Path(__file__).resolve().parents[1] / "data" / "processed" / "fred_monthly.csv"


def fetch(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urllib.request.urlopen(url, timeout=30) as r:
        txt = r.read().decode()
    df = pd.read_csv(io.StringIO(txt), parse_dates=["observation_date"])
    return df.set_index("observation_date")[series_id]


def main() -> None:
    print("Fetching from FRED (public CSV endpoint, no API key)...")
    raw = pd.concat([fetch(s) for s in SERIES], axis=1).dropna()
    print(f"  joined sample: {raw.index.min():%Y-%m} to {raw.index.max():%Y-%m} "
          f"({len(raw)} months)")

    out = raw.copy()
    # Stationary transforms, precomputed so the lab can focus on the test rather
    # than on data wrangling. Retail sales is a trending level series -> log
    # difference (monthly % growth). The other two are differenced in levels.
    out["retail_growth"] = np.log(raw["RSXFS"]).diff() * 100
    out["unrate_diff"] = raw["UNRATE"].diff()
    out["sentiment_diff"] = raw["UMCSENT"].diff()
    out = out.dropna().reset_index().rename(columns={"observation_date": "date"})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"  wrote {OUT.relative_to(Path.cwd())}  ({len(out)} rows, {len(out.columns)} cols)")
    print(f"  columns: {', '.join(out.columns)}")


if __name__ == "__main__":
    main()
