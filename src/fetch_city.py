# fetch_city.py
# Week 11 "The Tap": fetches every murder incident from the City of Dallas
# live Police Incidents feed (Dallas OpenData) and banks it in SQLite.
# Run it from the project's top folder:   python -m src.fetch_city
# Fetch once, query forever: the raw JSON is cached in data/, so a rerun
# rebuilds data/case.db without calling the API again.
# Writes data/case.db with two tables:
#     incidents   murder rows with a believable service year (2014 on)
#     quarantine  rows whose servyr is garbage (kept, never silently deleted)

import json
import os
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# Settings (ALL CAPS = a value that doesn't change)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw_incidents.json"   # Cache of the API's answer (gitignored)
DB_FILE = PROJECT_ROOT / "data" / "case.db"               # The case database (gitignored)

URL = "https://www.dallasopendata.com/resource/qv6i-rri7.json"   # Police Incidents, resource qv6i-rri7
# Murder rows: every offincident containing MURDER, plus plain HOMICIDE.
# Not nibrs_crime_category: it is only filled in from 2017 on.
MURDER_FILTER = "offincident like '%MURDER%' OR offincident = 'HOMICIDE'"
PAGE_SIZE = 5000                  # Rows per request
REQUEST_TIMEOUT_SECONDS = 60
FEED_START_YEAR = 2014            # The feed starts June 1, 2014; earlier servyr values are typos
TOKEN_NAME = "DALLAS_APP_TOKEN"   # Lives in .env at the repo root, never in Git


def fetch_page(offset, token):
    """Ask the API for one page of murder rows, starting at row number offset."""
    params = {
        "$where": MURDER_FILTER,
        "$order": "incidentnum",   # A stable order, so paging never repeats or skips rows
        "$limit": PAGE_SIZE,
        "$offset": offset,
        "$$app_token": token,      # Our own token: requests are not throttled (no HTTP 429 mid-lab)
    }
    # Params go in as a dict so requests URL-encodes the quotes and % signs (a hand-built URL gets HTTP 400)
    response = requests.get(URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()    # Fail loudly on a 400/429 instead of saving an error message as data
    return response.json()         # A list of dicts, one per incident


def fetch_all(token):
    """Return every murder row: from the cache if it exists, otherwise page through the API and cache it."""
    if RAW_FILE.exists():
        print(f"using cache {RAW_FILE.relative_to(PROJECT_ROOT)} (delete it to re-fetch)")
        return json.loads(RAW_FILE.read_text(encoding="utf-8"))
    rows, offset = [], 0
    while True:
        page = fetch_page(offset, token)
        rows.extend(page)
        print(f"offset {offset}: {len(page)} rows")
        if len(page) < PAGE_SIZE:  # A short page means we reached the end
            break
        offset += PAGE_SIZE
    RAW_FILE.parent.mkdir(exist_ok=True)
    RAW_FILE.write_text(json.dumps(rows), encoding="utf-8")
    print(f"saved {RAW_FILE.relative_to(PROJECT_ROOT)} ({len(rows)} rows)")
    return rows


def flatten(rows):
    """Turn the API's list of dicts into a table SQLite can store.

    geocoded_column is a nested dict, so it becomes two number columns (lat, lon).
    Columns starting with ":@" are the portal's computed regions and are dropped.
    servyr arrives as a string, so it becomes a number (garbage becomes NaN).
    """
    df = pd.DataFrame(rows)
    geo = df.pop("geocoded_column") if "geocoded_column" in df.columns else pd.Series(None, index=df.index)
    df["lat"] = geo.apply(lambda g: float(g["latitude"]) if isinstance(g, dict) else None)
    df["lon"] = geo.apply(lambda g: float(g["longitude"]) if isinstance(g, dict) else None)
    df = df[[c for c in df.columns if not c.startswith(":@")]]
    df["servyr"] = pd.to_numeric(df["servyr"], errors="coerce")
    return df


def split_bad_years(df, first=FEED_START_YEAR, last=None):
    """Split rows into (good, quarantined): servyr must be a year between first and last."""
    last = last or date.today().year
    good = df["servyr"].between(first, last)        # NaN is never "between", so it is quarantined too
    return df[good], df[~good]


def main():
    """Fetch (or load the cache), flatten, quarantine bad years, and write data/case.db."""
    load_dotenv(PROJECT_ROOT / ".env")             # Must run before reading the token
    token = os.environ[TOKEN_NAME]                 # KeyError here = .env is missing or has no token

    df = flatten(fetch_all(token))
    incidents, quarantine = split_bad_years(df)

    con = sqlite3.connect(DB_FILE)
    incidents.to_sql("incidents", con, if_exists="replace", index=False)
    quarantine.to_sql("quarantine", con, if_exists="replace", index=False)
    n = pd.read_sql("SELECT COUNT(*) AS n FROM incidents", con)["n"][0]
    print(f"case.db: {n} rows in incidents")
    print(f"case.db: {len(quarantine)} rows in quarantine (servyr outside {FEED_START_YEAR}-now)")
    if len(quarantine):
        print(quarantine[["incidentnum", "servyr", "offincident"]].to_string(index=False))
    con.close()


if __name__ == "__main__":     # Run main() only when this file is run directly
    main()
