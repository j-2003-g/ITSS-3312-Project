# test_factor.py
# Tests for src/factor.py, using made-up FBI responses (no network needed).

import pandas as pd
from src.factor import parse_pe, build_merged, run_models, model_numbers


def fake_payload():
    """A tiny FBI-shaped response: 2000-2002, with 2002's female count missing."""
    return {"actuals": {
        "Male Officers":    {"2000": 900, "2001": 800, "2002": 700},
        "Female Officers":  {"2000": 100, "2001": 100, "2002": None},
        "Male Civilians":   {"2000": 50,  "2001": 50,  "2002": 50},
        "Female Civilians": {"2000": 50,  "2001": 50,  "2002": 50},
    }}


def test_parse_pe_adds_officers_and_skips_half_counts():
    staffing = parse_pe(fake_payload())
    assert list(staffing.year) == [2000, 2001]            # 2002 skipped: female count missing
    assert list(staffing.sworn_total) == [1000, 900]
    assert list(staffing.civilians_total) == [100, 100]


def test_parse_pe_handles_old_response_shape():
    staffing = parse_pe(fake_payload()["actuals"])        # No "actuals" wrapper
    assert len(staffing) == 2


def test_lag_uses_previous_calendar_year_not_previous_row():
    series = pd.DataFrame({"year": [2000, 2001, 2003], "reported": [100, 50, 100],
                           "cleared": [50, 25, 60], "clearance": [0.5, 0.5, 0.6]})
    staffing = pd.DataFrame({"year": [2000, 2001, 2003], "sworn_total": [1000, 1000, 2000]})
    merged = build_merged(series, staffing).set_index("year")
    assert merged.loc[2000, "officers_per_100_homicides"] == 1000
    assert merged.loc[2001, "officers_per_100_homicides"] == 2000
    assert merged.loc[2001, "officers_per_100_homicides_lag1"] == 1000
    assert pd.isna(merged.loc[2003, "officers_per_100_homicides_lag1"])   # 2002 missing -> blank, not 2001


def test_models_run_and_recover_a_positive_slope():
    years = list(range(1990, 2010))
    officers = [1000 + 50 * i for i in range(20)]
    series = pd.DataFrame({"year": years, "reported": [100] * 20, "cleared": [0] * 20,
                           "clearance": [0.4 + 0.01 * i for i in range(20)]})
    staffing = pd.DataFrame({"year": years, "sworn_total": officers})
    models = run_models(build_merged(series, staffing))
    assert models["primary"].params["officers_per_100_homicides"] > 0
    assert int(models["lag1"].nobs) == 19                 # First year has no lag


def test_model_numbers_are_dashboard_ready():
    years = list(range(1990, 2010))
    series = pd.DataFrame({"year": years, "reported": [100] * 20, "cleared": [0] * 20,
                           "clearance": [0.4 + 0.01 * i for i in range(20)]})
    staffing = pd.DataFrame({"year": years, "sworn_total": [1000 + 50 * i for i in range(20)]})
    numbers = model_numbers(run_models(build_merged(series, staffing)))
    primary = numbers["primary"]
    assert primary["term"] == "officers_per_100_homicides"
    assert primary["factor_min"] == 1000 and primary["factor_max"] == 1950   # slider range
    assert primary["conf_int_95"][0] < primary["coef"] < primary["conf_int_95"][1]
    import json; json.dumps(numbers)                                          # must be JSON-safe


def test_fetch_skips_rejected_years(tmp_path, monkeypatch):
    """A decade the FBI rejects is retried year by year, keeping the good years."""
    import src.factor as factor

    class FakeResponse:
        def __init__(self, first, last):
            self.status_code = 400 if last >= 2025 else 200
            self.text = "Year not available" if self.status_code == 400 else ""
            self.first, self.last = first, last
        def raise_for_status(self):
            pass
        def json(self):
            years = range(self.first, self.last + 1)
            return {"actuals": {"Male Officers": {str(y): 3000 for y in years},
                                "Female Officers": {str(y): 500 for y in years}}}

    monkeypatch.setattr(factor, "FIRST_YEAR", 2015)
    monkeypatch.setattr(factor, "YEARS_PER_REQUEST", 5)            # 2015-19 ok, 2020-24 ok, 2025 rejected
    monkeypatch.setattr(factor, "LAST_YEAR", 2025)
    monkeypatch.setattr(factor.requests, "get",
                        lambda url, params, timeout: FakeResponse(params["from"], params["to"]))
    staffing = factor.fetch_staffing(tmp_path / "staffing.csv")
    assert list(staffing.year) == list(range(2015, 2025))          # 2025 skipped, the rest kept
    assert staffing["sworn_total"].dtype.kind == "i"               # Counts are numbers, not text
    assert (tmp_path / "staffing.csv").exists()


def test_text_counts_still_model_as_numbers():
    """Even if counts arrive as text, the regression gets one numeric slope, not categories."""
    years = list(range(1990, 2010))
    series = pd.DataFrame({"year": years, "reported": [100] * 20, "cleared": [0] * 20,
                           "clearance": [0.4 + 0.01 * i for i in range(20)]})
    staffing = pd.DataFrame({"year": years, "sworn_total": [str(1000 + 50 * i) for i in range(20)]},
                            dtype=object)
    models = run_models(build_merged(series, staffing))
    assert "officers_per_100_homicides" in models["primary"].params.index
