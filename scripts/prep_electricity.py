"""Fetch and cache hourly electricity demand for Lecture 3 (GAMs / Prophet).

Run once:  python scripts/prep_electricity.py
Writes:    data/processed/electricity_daily.csv   (2002-2018, one row per day)
           data/processed/electricity_hourly.csv  (2016-2018, one row per hour)

Why this dataset rather than M5: a GAM's selling point is several seasonal cycles at
once, and retail sales show essentially one. PJM East demand has three, and they are
all large:

    hour-of-day   ~34% swing   (4am trough -> 7pm peak)
    day-of-week   ~12% swing   (Sunday trough -> Tuesday peak)
    time-of-year  ~31% swing   (April trough -> July peak)

The annual cycle is also **double-peaked** - a July maximum from air conditioning and a
secondary January maximum from heating, with the minimum in the mild shoulder months.
That shape cannot be fitted by a linear term or a single harmonic, which is exactly the
argument for a smooth term.

Source: PJM Interconnection hourly metered load (PJME zone), via a public mirror of the
PJM data releases. PJM is the grid operator for 13 mid-Atlantic states and DC.
"""
from __future__ import annotations
import io
import urllib.request
from pathlib import Path

import pandas as pd

URL = ("https://raw.githubusercontent.com/panambY/Hourly_Energy_Consumption/"
       "master/data/PJME_hourly.csv")
OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
HOURLY_FROM = "2016-01-01"   # keeps the hourly file small enough to fit fast


def main() -> None:
    print("Fetching PJM East hourly demand...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = pd.read_csv(io.StringIO(r.read().decode()), parse_dates=["Datetime"])

    s = (raw.sort_values("Datetime")
            .drop_duplicates("Datetime")
            .set_index("Datetime")["PJME_MW"]
            .astype(float))
    print(f"  raw: {len(s):,} hours, {s.index.min():%Y-%m-%d} to {s.index.max():%Y-%m-%d}")

    # Reindex onto a complete hourly clock and fill the ~30 DST-related gaps.
    full = pd.date_range(s.index.min(), s.index.max(), freq="h")
    gaps = len(full) - len(s)
    s = s.reindex(full).interpolate(limit_direction="both")
    print(f"  filled {gaps} missing hours by interpolation")

    hourly = s.rename("mw").to_frame()
    hourly["hour"] = hourly.index.hour
    hourly["dow"] = hourly.index.dayofweek
    hourly["month"] = hourly.index.month
    hourly = hourly.loc[HOURLY_FROM:].reset_index(names="datetime")

    daily = s.resample("D").agg(["mean", "max", "min"])
    daily.columns = ["mw_mean", "mw_peak", "mw_trough"]
    daily["dow"] = daily.index.dayofweek
    daily["is_weekend"] = (daily.dow >= 5).astype(int)
    daily["doy"] = daily.index.dayofyear
    daily["month"] = daily.index.month
    daily["year"] = daily.index.year
    daily = daily.reset_index(names="date")

    OUT.mkdir(parents=True, exist_ok=True)
    daily.to_csv(OUT / "electricity_daily.csv", index=False)
    hourly.to_csv(OUT / "electricity_hourly.csv", index=False)
    print(f"  wrote electricity_daily.csv   {len(daily):,} rows "
          f"({daily.date.min():%Y-%m-%d} to {daily.date.max():%Y-%m-%d})")
    print(f"  wrote electricity_hourly.csv  {len(hourly):,} rows "
          f"(from {HOURLY_FROM})")


if __name__ == "__main__":
    main()
