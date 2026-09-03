"""
prep_favorita.py
----------------
Prepares the Favorita dataset for ECON 8310 **final projects**.

Favorita is not used in any lecture, lab or homework — it is the ready-made option
for a group that does not want to source its own data. See ECON8310_Datasets.md §4
and the project rubric.

The raw competition download is ~4.6 GB, and `train.csv` alone is about 125 million
rows. That is not something to hand a group in week four and wish them luck with.
This script reduces it to two files small enough to open in anything, while keeping
what makes the dataset worth using: promotions, the oil price, national holidays,
store metadata, and the April 2016 earthquake.

Source (a Kaggle account and accepting the competition rules are required):
  https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data

  kaggle competitions download -c favorita-grocery-sales-forecasting -p data/raw/
  unzip 'data/raw/*.zip' -d data/raw/

Input files (unzipped into data/raw/):
  train.csv             date, store_nbr, item_nbr, unit_sales, onpromotion  (~125M rows)
  stores.csv            store_nbr, city, state, type, cluster
  items.csv             item_nbr, family, class, perishable
  oil.csv               date, dcoilwtico
  holidays_events.csv   date, type, locale, description, transferred

Output files:
  data/processed/favorita_weekly.csv   store x family, weekly     (~430k rows)
  data/processed/favorita_daily.csv    one store x family, daily  (~1.7k rows)

Period: 2013-01-01 to 2017-08-15.

WHY STORE x FAMILY, AND WHY WEEKLY. Item level is 4,000 series, most of them mostly
zeros, which teaches sparsity rather than forecasting. Store x family gives 54 x 33
cells of which roughly 1,700 are populated and long — the same shape as the M5 spine
students already know, so the methods transfer while the data does not.

THE EARTHQUAKE IS LEFT IN, UNMARKED. 16 April 2016 is in the data with no flag on it.
A group that wants to study a structural break should find it in the series, not read
it from a column.

Run once, from the repository root:
  python scripts/prep_favorita.py
"""

import os
import sys

import numpy as np
import pandas as pd

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

REQUIRED = ["train.csv", "stores.csv", "items.csv", "oil.csv", "holidays_events.csv"]

# the single daily series, for a group that wants one series rather than a panel
DAILY_STORE = 44          # Quito, type A, cluster 5 — a large, complete store
DAILY_FAMILY = "GROCERY I"

# train.csv is ~125M rows; read it in pieces and aggregate as we go, so this runs
# on a laptop rather than needing 16 GB of RAM.
CHUNK = 5_000_000


def check_raw_files():
    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(RAW_DIR, f))]
    if missing:
        raise FileNotFoundError(
            f"Missing raw Favorita files: {missing}\n\n"
            "Favorita needs a Kaggle account, and you must accept the competition\n"
            "rules on the site before the download will work.\n\n"
            "  https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data\n\n"
            "With the Kaggle CLI installed and configured:\n"
            "  kaggle competitions download -c favorita-grocery-sales-forecasting "
            "-p data/raw/\n"
            "  unzip 'data/raw/*.zip' -d data/raw/\n\n"
            "The download is about 4.6 GB. You only do this once, and only if your\n"
            "group is using Favorita for the final project."
        )


def load_reference():
    stores = pd.read_csv(os.path.join(RAW_DIR, "stores.csv"))
    items = pd.read_csv(os.path.join(RAW_DIR, "items.csv"))

    oil = pd.read_csv(os.path.join(RAW_DIR, "oil.csv"), parse_dates=["date"])
    # The oil series is quoted on trading days only, so it has gaps at weekends and
    # holidays. Forward-fill: the price a forecaster could actually see on a Sunday
    # is Friday's close, not a missing value and not an interpolation from Monday.
    oil = oil.set_index("date").asfreq("D")
    oil["dcoilwtico"] = oil["dcoilwtico"].ffill()
    oil = oil.reset_index()

    hol = pd.read_csv(os.path.join(RAW_DIR, "holidays_events.csv"), parse_dates=["date"])
    # A transferred holiday did not happen on its nominal date, so it is not a holiday
    # for forecasting purposes; the "Transfer" row that replaces it is.
    hol = hol[~hol["transferred"]]
    national = (hol[hol["locale"] == "National"]
                .groupby("date").size().rename("is_holiday").reset_index())
    national["is_holiday"] = 1
    return stores, items, oil, national


def aggregate_sales(items):
    """Sum unit_sales and count promotions per store x family x day, in chunks."""
    fam = items.set_index("item_nbr")["family"]
    parts = []
    path = os.path.join(RAW_DIR, "train.csv")
    print("Aggregating train.csv in chunks (this is the slow part)...")
    for i, chunk in enumerate(pd.read_csv(
            path, usecols=["date", "store_nbr", "item_nbr", "unit_sales", "onpromotion"],
            parse_dates=["date"], chunksize=CHUNK)):
        chunk["family"] = chunk["item_nbr"].map(fam)
        # Returns are recorded as negative unit_sales. Clipping at zero would hide
        # them; they are real and a project may want them, so they are kept.
        chunk["onpromotion"] = chunk["onpromotion"].fillna(False).astype(bool)
        g = (chunk.groupby(["date", "store_nbr", "family"], observed=True)
                  .agg(unit_sales=("unit_sales", "sum"),
                       n_promo=("onpromotion", "sum"),
                       n_items=("item_nbr", "size"))
                  .reset_index())
        parts.append(g)
        print(f"  chunk {i + 1}: {len(chunk):>10,} rows -> {len(g):>7,} cells")
    daily = (pd.concat(parts, ignore_index=True)
               .groupby(["date", "store_nbr", "family"], observed=True)
               .sum().reset_index())
    return daily


def attach_context(df, stores, oil, national):
    df = df.merge(stores, on="store_nbr", how="left")
    df = df.merge(oil, on="date", how="left")
    df = df.merge(national, on="date", how="left")
    df["is_holiday"] = df["is_holiday"].fillna(0).astype(int)
    df["dow"] = df["date"].dt.dayofweek
    return df


def to_weekly(daily):
    d = daily.copy()
    d["week_start"] = d["date"] - pd.to_timedelta(d["date"].dt.dayofweek, unit="D")
    w = (d.groupby(["week_start", "store_nbr", "family"], observed=True)
           .agg(unit_sales=("unit_sales", "sum"),
                n_promo=("n_promo", "sum"),
                holiday_days=("is_holiday", "sum"),
                avg_oil=("dcoilwtico", "mean"),
                city=("city", "first"), state=("state", "first"),
                store_type=("type", "first"), cluster=("cluster", "first"))
           .reset_index())
    # Drop partial weeks at either end so no series starts or ends on a stub.
    full = w.groupby("week_start")["store_nbr"].size()
    keep = full[full >= full.max() * 0.5].index
    return w[w["week_start"].isin(keep)].copy()


def build():
    check_raw_files()
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    stores, items, oil, national = load_reference()
    daily = aggregate_sales(items)
    daily = attach_context(daily, stores, oil, national)

    print("\nWriting weekly panel...")
    weekly = to_weekly(daily).sort_values(["store_nbr", "family", "week_start"])
    weekly.to_csv(os.path.join(PROCESSED_DIR, "favorita_weekly.csv"), index=False)

    print(f"Writing daily series (store {DAILY_STORE} x {DAILY_FAMILY})...")
    one = (daily[(daily["store_nbr"] == DAILY_STORE) &
                 (daily["family"] == DAILY_FAMILY)]
           .sort_values("date")
           [["date", "unit_sales", "n_promo", "is_holiday", "dcoilwtico", "dow"]])
    # Fail rather than write an empty file. An empty CSV is the worst outcome here:
    # the script exits 0, the file exists, and the problem surfaces days later inside
    # somebody's model. Caught by a test fixture that happened not to contain store 44.
    if one.empty:
        raise ValueError(
            f"No rows for store {DAILY_STORE} x {DAILY_FAMILY} — favorita_daily.csv "
            f"would have been empty.\n"
            f"  stores present:   {sorted(daily['store_nbr'].unique())[:12]}...\n"
            f"  families present: {sorted(daily['family'].dropna().unique())[:6]}...\n"
            f"Edit DAILY_STORE / DAILY_FAMILY at the top of this script."
        )
    one.to_csv(os.path.join(PROCESSED_DIR, "favorita_daily.csv"), index=False)

    n_series = weekly.groupby(["store_nbr", "family"]).ngroups
    per = weekly.groupby(["store_nbr", "family"]).size()
    print("\nDone.")
    print(f"  favorita_weekly.csv  {len(weekly):>7,} rows | {n_series:,} store-family series "
          f"| {weekly.week_start.min().date()} to {weekly.week_start.max().date()}")
    print(f"  favorita_daily.csv   {len(one):>7,} rows | 1 series "
          f"| {one.date.min().date()} to {one.date.max().date()}")
    print(f"\n  Weeks per series: min {per.min()}, median {int(per.median())}, max {per.max()}")
    quake = weekly[(weekly.week_start >= "2016-04-11") & (weekly.week_start <= "2016-04-18")]
    if len(quake):
        print(f"  The week of the 16 April 2016 earthquake is present and unflagged "
              f"({len(quake):,} rows) — find it in the series, not in a column.")


if __name__ == "__main__":
    try:
        build()
    except (FileNotFoundError, ValueError) as e:
        print(f"\n{e}\n", file=sys.stderr)
        sys.exit(1)
