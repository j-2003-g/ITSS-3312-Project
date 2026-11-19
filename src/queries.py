# queries.py
# Week 11 "The Tap": asks data/case.db three questions, then lines the city's
# per-year counts up against the week 9 FBI series (the reporting-gap audit).
# Run it from the project's top folder (after python -m src.fetch_city):
#     python -m src.queries

import sqlite3
from pathlib import Path

import pandas as pd

# Settings (ALL CAPS = a value that doesn't change)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_ROOT / "data" / "case.db"
SERIES_FILE = PROJECT_ROOT / "reports" / "dallas_series.csv"   # Week 9: FBI counts via MAP

FIRST_YEAR = 2014           # The city feed starts June 1, 2014
LAST_YEAR = 2026            # Current year (partial)
TOP_BEATS = 5
# Our squad's slice: the Southeast patrol division. Week 10's map showed the
# open/no-arrest cases pooling in southeast Dallas; this asks whether the
# city's own feed puts the same weight there.
SLICE_DIVISION = "SOUTHEAST"

# Q1: murders per year. One row per victim (an incident with two victims has
# two rows with the same incidentnum), so COUNT(*) counts victims, like the FBI's MRD.
MURDERS_PER_YEAR = """
    SELECT servyr AS year,
           COUNT(*) AS murders,
           COUNT(DISTINCT incidentnum) AS incidents
    FROM incidents
    WHERE servyr BETWEEN ? AND ?
    GROUP BY servyr
    ORDER BY servyr"""

# Q2: the five beats with the most murders since 2014 (ties broken by beat number)
TOP_5_BEATS = """
    SELECT beat, division, COUNT(*) AS murders
    FROM incidents
    WHERE beat IS NOT NULL
    GROUP BY beat, division
    ORDER BY murders DESC, beat
    LIMIT ?"""

# Q3: our slice, the share of all murders that happened in one division
DIVISION_SHARE = """
    SELECT ? AS division,
           SUM(division = ?) AS murders,
           COUNT(*) AS all_murders,
           ROUND(100.0 * SUM(division = ?) / COUNT(*), 1) AS pct
    FROM incidents"""


def murders_per_year(con, first=FIRST_YEAR, last=LAST_YEAR):
    """Q1: murders (victim rows) and distinct incidents per service year."""
    return pd.read_sql(MURDERS_PER_YEAR, con, params=(first, last))


def top_beats(con, n=TOP_BEATS):
    """Q2: the n beats with the most murders."""
    return pd.read_sql(TOP_5_BEATS, con, params=(n,))


def division_share(con, division=SLICE_DIVISION):
    """Q3: how many murders, and what percent of all of them, happened in one division."""
    return pd.read_sql(DIVISION_SHARE, con, params=(division, division, division))


def compare_to_fbi(city, fbi):
    """Line the city's per-year murders up against the FBI's (week 9) for the years both cover.

    city_pct_of_fbi is how much of the FBI count shows up in the city's public feed.
    """
    both = city.merge(fbi[["year", "reported"]], on="year", how="inner")
    both = both.rename(columns={"murders": "city_feed", "reported": "fbi_mrd"})
    both["gap"] = both["fbi_mrd"] - both["city_feed"]
    both["city_pct_of_fbi"] = (100 * both["city_feed"] / both["fbi_mrd"]).round(0).astype(int)
    return both[["year", "fbi_mrd", "city_feed", "gap", "city_pct_of_fbi"]]


def main():
    """Print the three answers and the FBI-versus-city comparison."""
    con = sqlite3.connect(DB_FILE)
    total = pd.read_sql("SELECT COUNT(*) AS n FROM incidents", con)["n"][0]
    print(f"SELECT COUNT(*) FROM incidents -> {total}\n")

    per_year = murders_per_year(con)
    print(f"Q1: MURDERS PER YEAR, {FIRST_YEAR}-{LAST_YEAR} "
          f"({FIRST_YEAR} starts June 1; {LAST_YEAR} is partial)")
    print(per_year.to_string(index=False), "\n")

    print(f"Q2: TOP {TOP_BEATS} BEATS SINCE {FIRST_YEAR}")
    print(top_beats(con).to_string(index=False), "\n")

    print(f"Q3: OUR SLICE, SHARE OF MURDERS IN THE {SLICE_DIVISION} DIVISION")
    print(division_share(con).to_string(index=False), "\n")
    con.close()

    print("CITY FEED VS FBI (week 9 reports/dallas_series.csv), years both cover")
    fbi = pd.read_csv(SERIES_FILE)
    comparison = compare_to_fbi(per_year, fbi)
    print(comparison.to_string(index=False))
    print(f"\ntotal: city feed {comparison['city_feed'].sum()} vs FBI {comparison['fbi_mrd'].sum()} "
          f"({100 * comparison['city_feed'].sum() / comparison['fbi_mrd'].sum():.0f}%)")


if __name__ == "__main__":     # Run main() only when this file is run directly
    main()
