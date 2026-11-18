# factor.py
# Week 12 "The Factor": does Dallas PD staffing line up with homicide clearance?
#
# Pre-registered hypothesis (locked at standup):
#   Dallas PD sworn officers per homicide is associated with Dallas homicide
#   clearance, in the positive direction. We also test a one-year lag, because
#   of the 2016-17 pension-driven exodus of veteran officers.
#
# Run it from the project's top folder:   python -m src.factor
#   1. Downloads Dallas PD's yearly staffing from the FBI Crime Data Explorer
#      (no API key needed) into data/dpd_staffing.csv, unless it's already there.
#   2. Merges it with reports/dallas_series.csv (week 9) on year.
#   3. Runs the pre-registered regression, the lag-1 variant, and one
#      confounder check, and saves all three summaries to reports/factor_results.txt.
#   4. Saves the merged table (reports/factor_merged.csv) and each model's
#      numbers (reports/factor_model.json) for the week 14 dashboard.

from pathlib import Path
import pandas as pd
import json
import requests
import statsmodels.formula.api as smf

# Settings (ALL CAPS = a value that doesn't change)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERIES_FILE = PROJECT_ROOT / "reports" / "dallas_series.csv"
STAFFING_FILE = PROJECT_ROOT / "data" / "dpd_staffing.csv"
RESULTS_FILE = PROJECT_ROOT / "reports" / "factor_results.txt"
# Saved for the week 14 app, which only reads reports/ and computes nothing new
MERGED_FILE = PROJECT_ROOT / "reports" / "factor_merged.csv"
MODEL_FILE = PROJECT_ROOT / "reports" / "factor_model.json"

# FBI Crime Data Explorer, police employee ("pe") endpoint: /pe/{state}/{ORI}.
# The FBI uses Dallas PD's 9-character ORI here (TXDPD0000), not the
# 7-character TXDPD00 in the MAP file. No API key is needed on this host.
CDE_URL = "https://cde.ucr.cjis.gov/LATEST/pe/TX/TXDPD0000"
FIRST_YEAR = 1965             # Same window as the week 9 series
LAST_YEAR = 2025
DOWNLOAD_TIMEOUT_SECONDS = 120
SOURCE_NOTE = "FBI Crime Data Explorer, Law Enforcement Employees, ORI TXDPD0000"

# Supplement anchors: roughly what our table should show (sworn officers)
STAFFING_ANCHORS = {2010: 3597, 2018: 3007, 2024: 3120}
ANCHOR_TOLERANCE = 0.10       # Within 10% counts as "matches"

PER_HOMICIDES = 100           # Officers per 100 homicides (the deck's own framing)


def parse_pe(payload):
    """Turn the FBI's police-employee JSON into one row per year: year, sworn_total, civilians_total.

    The FBI nests counts as {category -> {year -> value}}, under "actuals"
    (older responses put the categories at the top level).
    """
    categories = payload.get("actuals", payload)
    def series(label):
        values = categories.get(label) or {}
        return {int(year): value for year, value in values.items() if value is not None}

    male_officers = series("Male Officers")
    female_officers = series("Female Officers")
    male_civilians = series("Male Civilians")
    female_civilians = series("Female Civilians")

    rows = []
    for year in sorted(set(male_officers) | set(female_officers)):
        if year not in male_officers or year not in female_officers:
            continue                    # Half a count is not a count: skip, don't guess
        rows.append({
            "year": year,
            "sworn_total": int(male_officers[year] + female_officers[year]),
            "civilians_total": (int(male_civilians[year] + female_civilians[year])
                                if year in male_civilians and year in female_civilians else None),
        })
    return pd.DataFrame(rows, columns=["year", "sworn_total", "civilians_total"])


def fetch_staffing(path=STAFFING_FILE):
    """Download Dallas PD staffing to data/dpd_staffing.csv (or reuse the cached copy) and return it."""
    if path.exists():
        print(f"cached: {path.name}")
        return pd.read_csv(path)
    response = requests.get(CDE_URL, params={"from": FIRST_YEAR, "to": LAST_YEAR},
                            timeout=DOWNLOAD_TIMEOUT_SECONDS)
    response.raise_for_status()
    staffing = parse_pe(response.json())
    if staffing.empty:
        raise ValueError("The FBI returned no staffing rows for TXDPD0000. Check the URL and ORI.")
    staffing["source"] = SOURCE_NOTE
    path.parent.mkdir(exist_ok=True)
    staffing.to_csv(path, index=False)
    print(f"saved: {path.name} ({len(staffing)} years)")
    return staffing


def check_anchors(staffing):
    """Print how our sworn counts compare with the supplement's known anchors."""
    sworn = staffing.set_index("year")["sworn_total"]
    for year, expected in STAFFING_ANCHORS.items():
        if year not in sworn.index:
            print(f"  {year}: missing (expected about {expected:,})")
            continue
        ok = abs(sworn[year] - expected) / expected <= ANCHOR_TOLERANCE
        print(f"  {year}: {sworn[year]:,} sworn (expected about {expected:,}) {'OK' if ok else 'CHECK THIS'}")


def build_merged(series, staffing):
    """Merge clearance and staffing on year, add officers per 100 homicides and its one-year lag.

    The lag is taken from the PREVIOUS CALENDAR YEAR's row, not the previous
    row, so a missing year gives a blank lag instead of a wrong one.
    """
    series = series.astype({"year": int})
    staffing = staffing.astype({"year": int})
    merged = series.merge(staffing[["year", "sworn_total"]], on="year", how="inner")
    merged["officers_per_100_homicides"] = merged["sworn_total"] / merged["reported"] * PER_HOMICIDES
    previous = merged[["year", "officers_per_100_homicides"]].rename(
        columns={"officers_per_100_homicides": "officers_per_100_homicides_lag1"})
    previous["year"] = previous["year"] + 1
    return merged.merge(previous, on="year", how="left")


def run_models(merged):
    """Return the three fitted models: pre-registered, lag-1, and the shared-denominator check."""
    primary = smf.ols("clearance ~ officers_per_100_homicides", data=merged).fit()
    lagged = smf.ols("clearance ~ officers_per_100_homicides_lag1",
                     data=merged.dropna(subset=["officers_per_100_homicides_lag1"])).fit()
    # Confounder check, NOT the hypothesis: officers per homicide and clearance
    # share the same denominator (homicides). If raw sworn strength shows the
    # same story, the result isn't just homicide spikes moving both numbers.
    check = smf.ols("clearance ~ sworn_total", data=merged).fit()
    return {"primary": primary, "lag1": lagged, "check_sworn_total": check}


def one_line(name, model, term):
    """Short summary: coef, p-value, R-squared and n for one term."""
    return (f"{name}: coef = {model.params[term]:.5f}, p = {model.pvalues[term]:.4f}, "
            f"R² = {model.rsquared:.3f}, n = {int(model.nobs)}")


def model_numbers(models):
    """Every number the dashboard needs from each model, as plain JSON-ready values."""
    out = {}
    for name, model in models.items():
        term = [t for t in model.params.index if t != "Intercept"][0]
        out[name] = {
            "formula": f"clearance ~ {term}",
            "term": term,
            "intercept": float(model.params["Intercept"]),
            "coef": float(model.params[term]),
            "p_value": float(model.pvalues[term]),
            "r_squared": float(model.rsquared),
            "n": int(model.nobs),
            "conf_int_95": [float(v) for v in model.conf_int().loc[term]],
            "factor_min": float(model.model.exog[:, 1].min()),   # What-If slider range:
            "factor_max": float(model.model.exog[:, 1].max()),   # stay inside the data
        }
    return out


def save_for_dashboard(merged, models, years):
    """Write the merged table and the model numbers that src/app.py will read."""
    merged.to_csv(MERGED_FILE, index=False)
    payload = {"hypothesis": "Dallas PD sworn officers per homicide is associated with Dallas "
                             "homicide clearance, in the positive direction (plus a one-year lag).",
               "clearance_definition": "FBI: cleared by arrest or exceptional means, "
                                       "counted in the year the clearance happens",
               "staffing_source": SOURCE_NOTE,
               "years": years,
               "models": model_numbers(models)}
    MODEL_FILE.write_text(json.dumps(payload, indent=2))


def main():
    """Fetch, merge, eyeball, model, and save the summaries."""
    series = pd.read_csv(SERIES_FILE)
    staffing = fetch_staffing()
    print("\nStaffing anchors:")
    check_anchors(staffing)

    merged = build_merged(series, staffing)
    print(f"\nMerged shape: {merged.shape}  (years {merged.year.min()}-{merged.year.max()})")
    print(merged.head())                               # Eyeball before modeling

    models = run_models(merged)
    lines = [
        one_line("PRIMARY  clearance ~ officers_per_100_homicides", models["primary"], "officers_per_100_homicides"),
        one_line("LAG-1    clearance ~ officers_per_100_homicides_lag1", models["lag1"], "officers_per_100_homicides_lag1"),
        one_line("CHECK    clearance ~ sworn_total", models["check_sworn_total"], "sworn_total"),
    ]
    print("\n" + "\n".join(lines))

    with open(RESULTS_FILE, "w") as file:
        file.write("WEEK 12 FACTOR RESULTS (generated by python -m src.factor)\n")
        file.write(f"Staffing source: {SOURCE_NOTE}\n")
        file.write(f"Merged years: {merged.year.min()}-{merged.year.max()}, n = {len(merged)}\n\n")
        file.write("\n".join(lines) + "\n")
        for name, model in models.items():
            file.write(f"\n\n===== {name} =====\n{model.summary()}\n")
    save_for_dashboard(merged, models, [int(merged.year.min()), int(merged.year.max())])
    for path in (RESULTS_FILE, MERGED_FILE, MODEL_FILE):
        print(f"wrote {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
