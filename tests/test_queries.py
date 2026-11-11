# test_queries.py
# Tests for src/queries.py, using a tiny in-memory case database (no fetch needed).

import sqlite3
import pandas as pd
from src.queries import murders_per_year, top_beats, division_share, compare_to_fbi


def make_db():
    """Fake incidents table: 2015 has one incident with two victims (two rows, same incidentnum)."""
    con = sqlite3.connect(":memory:")
    pd.DataFrame({
        "incidentnum": ["A-2015", "A-2015", "B-2015", "C-2016", "D-2013"],
        "servyr":      [2015, 2015, 2015, 2016, 2013],
        "beat":        ["346", "346", "153", "346", "153"],
        "division":    ["SOUTHEAST", "SOUTHEAST", "CENTRAL", "SOUTHEAST", "CENTRAL"],
    }).to_sql("incidents", con, index=False)
    return con


def test_murders_per_year_counts_victims_and_incidents():
    per_year = murders_per_year(make_db(), first=2014, last=2016)
    assert per_year["year"].tolist() == [2015, 2016]             # 2013 is outside the range
    assert per_year["murders"].tolist() == [3, 1]                # Victim rows
    assert per_year["incidents"].tolist() == [2, 1]              # Distinct incident numbers


def test_top_beats_ranks_most_first():
    beats = top_beats(make_db(), n=1)
    assert beats["beat"].tolist() == ["346"]
    assert beats["murders"].tolist() == [3]


def test_division_share():
    share = division_share(make_db(), "SOUTHEAST")
    assert share.loc[0, "murders"] == 3
    assert share.loc[0, "pct"] == 60.0                           # 3 of 5


def test_compare_to_fbi_keeps_overlap_years_only():
    city = pd.DataFrame({"year": [2015, 2016, 2026], "murders": [50, 60, 10]})
    fbi = pd.DataFrame({"year": [2014, 2015, 2016], "reported": [100, 100, 120]})
    both = compare_to_fbi(city, fbi)
    assert both["year"].tolist() == [2015, 2016]
    assert both["gap"].tolist() == [50, 60]
    assert both["city_pct_of_fbi"].tolist() == [50, 50]
