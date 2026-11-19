# test_fetch_city.py
# Tests for src/fetch_city.py, using made-up API rows (no network, no token needed).

import sqlite3
from src.fetch_city import flatten, split_bad_years


def make_rows():
    """Three fake API rows: one geocoded, one without coordinates, one with a garbage servyr."""
    return [
        {"incidentnum": "000001-2015", "servyr": "2015", "beat": "346",
         "geocoded_column": {"latitude": "32.7", "longitude": "-96.8"},
         ":@computed_region_abcd": "12"},
        {"incidentnum": "000002-2020", "servyr": "2020", "beat": "153"},
        {"incidentnum": "000003-1011", "servyr": "1011", "beat": "257",
         "geocoded_column": {"latitude": "32.9", "longitude": "-96.7"}},
    ]


def test_flatten_unpacks_geocoded_column():
    df = flatten(make_rows())
    assert "geocoded_column" not in df.columns
    assert df.loc[0, "lat"] == 32.7 and df.loc[0, "lon"] == -96.8
    assert df["lat"].isna()[1]                                   # No coordinates -> missing, not a crash


def test_flatten_drops_computed_regions_and_converts_servyr():
    df = flatten(make_rows())
    assert not any(c.startswith(":@") for c in df.columns)
    assert df["servyr"].tolist() == [2015, 2020, 1011]           # Strings became numbers


def test_flattened_rows_fit_in_sqlite():
    con = sqlite3.connect(":memory:")
    flatten(make_rows()).to_sql("incidents", con, index=False)  # A dict column would fail here
    assert con.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 3


def test_bad_years_are_quarantined_not_dropped():
    df = flatten(make_rows())
    good, quarantine = split_bad_years(df, first=2014, last=2026)
    assert good["incidentnum"].tolist() == ["000001-2015", "000002-2020"]
    assert quarantine["incidentnum"].tolist() == ["000003-1011"]
    assert len(good) + len(quarantine) == len(df)                # Nothing silently deleted
