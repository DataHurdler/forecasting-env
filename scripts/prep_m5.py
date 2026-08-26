"""
prep_m5.py
----------
Prepares the M5 / Walmart dataset for ECON 8310 lectures, labs, and homework.

The M5 competition data is the course spine (see
quality_reports/decisions/ADR-0001-course-dataset-architecture.md). The raw
download is ~460 MB across three files; this script subsets and aggregates it
into two small CSVs that every assignment reads.

Source (free, no Kaggle account needed):
  https://github.com/Nixtla/m5-forecasts/raw/main/datasets/m5.zip   (~48 MB)
  mirror: https://zenodo.org/records/10203108

Input files (place unzipped in data/raw/):
  data/raw/sales_train_evaluation.csv   wide: one row per item-store, d_1..d_1941
  data/raw/calendar.csv                 date, events, SNAP flags
  data/raw/sell_prices.csv              weekly price per store-item

Output files:
  data/processed/m5_weekly.csv   30 series (10 stores x 3 categories), weekly
  data/processed/m5_daily.csv    1 series (CA_1 x FOODS), daily -- for GAMs/Prophet

Period: 2011-01-29 to 2016-06-19 (1,941 days ~= 277 weeks)

Why store x category and not item level: 30 series matches the scale students
can reason about, every series is long and non-sparse, and the store/category
split gives a real two-level hierarchy for the Bayesian lectures.

Run once before any assignment:
  python scripts/prep_m5.py
"""

import os
import sys
import pandas as pd
import numpy as np

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

REQUIRED = ["sales_train_evaluation.csv", "calendar.csv", "sell_prices.csv"]

# the daily series used by the GAM / Prophet assignment
DAILY_STORE = "CA_1"
DAILY_CAT = "FOODS"


# ── checks ───────────────────────────────────────────────────────────────────

def check_raw_files():
    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(RAW_DIR, f))]
    if missing:
        raise FileNotFoundError(
            f"Missing raw M5 files: {missing}\n\n"
            "Download and unzip into data/raw/:\n"
            "  curl -L -o m5.zip "
            "https://github.com/Nixtla/m5-forecasts/raw/main/datasets/m5.zip\n"
            "  unzip m5.zip -d data/raw/\n\n"
            "Mirror (individual CSVs): https://zenodo.org/records/10203108"
        )


# ── load and aggregate ───────────────────────────────────────────────────────

def load_calendar():
    cal = pd.read_csv(os.path.join(RAW_DIR, "calendar.csv"), parse_dates=["date"])
    cal["is_event"] = cal["event_name_1"].notna().astype(int)

    # The Nixtla mirror drops the `d` column that the Kaggle release carries, so
    # rebuild it: the calendar is one row per consecutive day starting at d_1.
    if "d" not in cal.columns:
        cal = cal.sort_values("date").reset_index(drop=True)
        cal["d"] = "d_" + (cal.index + 1).astype(str)
    return cal


def aggregate_sales():
    """Wide item-level sales -> long store x category x day.

    Aggregating BEFORE melting matters: melting the raw 30k x 1941 frame first
    would produce ~59M rows. Aggregating first gives 30 rows, then 58k after melt.
    """
    sales = pd.read_csv(os.path.join(RAW_DIR, "sales_train_evaluation.csv"))
    day_cols = [c for c in sales.columns if c.startswith("d_")]

    agg = sales.groupby(["store_id", "cat_id"], as_index=False)[day_cols].sum()

    long = agg.melt(
        id_vars=["store_id", "cat_id"],
        value_vars=day_cols,
        var_name="d",
        value_name="units",
    )
    return long


def category_prices():
    """Mean sell price per store x category x retail week.

    cat_id is not a column in sell_prices, but item_id encodes it as a prefix
    (e.g. FOODS_3_090), so it can be derived without a join back to the sales file.
    """
    prices = pd.read_csv(
        os.path.join(RAW_DIR, "sell_prices.csv"),
        dtype={"store_id": "category", "item_id": "str",
               "wm_yr_wk": "int32", "sell_price": "float32"},
    )
    prices["cat_id"] = prices["item_id"].str.split("_").str[0]
    out = (prices.groupby(["store_id", "cat_id", "wm_yr_wk"], observed=True)["sell_price"]
                 .mean().reset_index().rename(columns={"sell_price": "avg_price"}))
    return out


def add_lags(df, group_cols, value_col, lags):
    for L in lags:
        df[f"{value_col}_lag{L}"] = df.groupby(group_cols, observed=True)[value_col].shift(L)
    return df


# ── build ────────────────────────────────────────────────────────────────────

def build():
    check_raw_files()
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    print("Loading calendar...")
    cal = load_calendar()

    print("Aggregating sales to store x category x day...")
    long = aggregate_sales()
    long = long.merge(cal[["d", "date", "wm_yr_wk", "wday", "month", "year",
                           "is_event", "snap_CA", "snap_TX", "snap_WI"]],
                      on="d", how="left")

    # SNAP is state-specific; pick the column matching each store's state
    long["state_id"] = long["store_id"].str.split("_").str[0]
    snap = {"CA": "snap_CA", "TX": "snap_TX", "WI": "snap_WI"}
    long["snap"] = [row[snap[st]] for st, row in
                    zip(long["state_id"], long[["snap_CA", "snap_TX", "snap_WI"]].to_dict("records"))]
    long = long.drop(columns=["snap_CA", "snap_TX", "snap_WI"])

    print("Merging prices...")
    prices = category_prices()
    long = long.merge(prices, on=["store_id", "cat_id", "wm_yr_wk"], how="left")

    long = long.sort_values(["store_id", "cat_id", "date"]).reset_index(drop=True)

    # ---------- daily output (single series, for GAMs / Prophet) -------------
    print(f"Writing daily series ({DAILY_STORE} x {DAILY_CAT})...")
    daily = long[(long.store_id == DAILY_STORE) & (long.cat_id == DAILY_CAT)].copy()
    daily = daily[["date", "store_id", "cat_id", "units", "avg_price",
                   "snap", "is_event", "wday", "month", "year"]]
    daily = add_lags(daily, ["store_id", "cat_id"], "units", [1, 7, 14, 28, 365])
    daily.to_csv(os.path.join(PROCESSED_DIR, "m5_daily.csv"), index=False)

    # ---------- weekly output (30 series) -----------------------------------
    print("Aggregating to weekly...")
    long["week_start"] = long["date"] - pd.to_timedelta(long["date"].dt.dayofweek, unit="D")
    weekly = (long.groupby(["store_id", "cat_id", "state_id", "week_start"], observed=True)
                  .agg(units=("units", "sum"),
                       avg_price=("avg_price", "mean"),
                       snap_days=("snap", "sum"),
                       event_days=("is_event", "sum"))
                  .reset_index())

    # drop partial weeks at both ends so every row is a full 7 days
    counts = (long.groupby(["store_id", "cat_id", "week_start"], observed=True)
                  .size().rename("n_days").reset_index())
    weekly = weekly.merge(counts, on=["store_id", "cat_id", "week_start"])
    weekly = weekly[weekly.n_days == 7].drop(columns=["n_days"])

    weekly = weekly.sort_values(["store_id", "cat_id", "week_start"]).reset_index(drop=True)
    weekly = add_lags(weekly, ["store_id", "cat_id"], "units", [1, 2, 3, 4, 52])
    weekly.to_csv(os.path.join(PROCESSED_DIR, "m5_weekly.csv"), index=False)

    # ---------- report -------------------------------------------------------
    n_series = weekly.groupby(["store_id", "cat_id"], observed=True).ngroups
    per = weekly.groupby(["store_id", "cat_id"], observed=True).size()
    print("\nDone.")
    print(f"  m5_weekly.csv  {len(weekly):>7,} rows | {n_series} series "
          f"| {per.min()}-{per.max()} weeks each")
    print(f"  m5_daily.csv   {len(daily):>7,} rows | 1 series "
          f"| {daily.date.min().date()} to {daily.date.max().date()}")
    print(f"\n  Holt-Winters check: {per.min()} weeks per series, "
          f"52-week season needs 104 -> "
          f"{'OK' if per.min() >= 104 else 'TOO SHORT'}")


if __name__ == "__main__":
    try:
        build()
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
