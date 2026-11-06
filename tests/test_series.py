# test_series.py
# Tests for src/series.py, using a tiny made-up archive (no download needed).

import pandas as pd
from src.series import (build_series, over_100_percent, missing_years,
                        biggest_jumps, suspicious_years, DALLAS_PD_ORI)


def make_archive():
    """Tiny fake MAP archive: Dallas PD for 2000-2003 (2002 missing), plus a Dallas, GA decoy."""
    return pd.DataFrame({
        "ORI":    [DALLAS_PD_ORI, DALLAS_PD_ORI, DALLAS_PD_ORI, "GA11000"],
        "Agency": ["Dallas", "Dallas", "Dallas", "Dallas"],
        "YEAR":   [2000, 2001, 2003, 2000],
        "MRD":    [100, 50, 10, 999],
        "CLR":    [50, 60, 4, 999],
        "Source": ["FBI", "FBI", "MAP", "FBI"],
    })


def test_filter_on_ori_not_agency_name():
    df = make_archive()
    dallas = df[df["ORI"] == DALLAS_PD_ORI]
    assert len(dallas) == 3                       # The Georgia "Dallas" is excluded
    assert (df["Agency"] == "Dallas").sum() == 4  # Filtering on the name would have kept it


def test_series_columns_and_rate():
    df = make_archive()
    per_year = build_series(df[df["ORI"] == DALLAS_PD_ORI])
    assert list(per_year.columns) == ["reported", "cleared", "clearance"]
    assert per_year.index.name == "year"
    assert per_year.loc[2000, "clearance"] == 0.5


def test_sanity_checks_find_problems():
    df = make_archive()
    dallas = df[df["ORI"] == DALLAS_PD_ORI]
    per_year = build_series(dallas)
    assert list(over_100_percent(per_year).index) == [2001]      # 60 cleared / 50 reported = 120%
    assert missing_years(per_year, 2000, 2003) == [2002]
    assert biggest_jumps(per_year, 1).index[0] in (2001, 2003)
    flagged = [year for year, _ in suspicious_years(per_year, dallas, last=2003)]
    assert flagged[0] == 2001                                    # Over 100% is flagged first
    assert 2003 in flagged                                       # Partial year + MAP-sourced
