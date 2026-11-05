# series.py
# Week 9 "First Cut": builds Dallas PD's homicide clearance series from MAP's
# FBI archive and flags the years that look wrong.
# Run it from the project's top folder (after python -m src.get_data):
#     python -m src.series
# Writes reports/dallas_series.csv with columns: year, reported, cleared, clearance

from pathlib import Path
import pandas as pd

# Settings (ALL CAPS = a value that doesn't change)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAP_FILE = PROJECT_ROOT / "data" / "map_ucr.csv"
WAPO_DALLAS_FILE = PROJECT_ROOT / "data" / "wapo_dallas.csv"
SERIES_FILE = PROJECT_ROOT / "reports" / "dallas_series.csv"

DALLAS_PD_ORI = "TXDPD00"     # FBI agency ID for Dallas PD. Filter on this, NOT on "Agency":
                              # four US agencies are called "Dallas" (TX, GA, NC, OR).
FIRST_YEAR = 1965             # First year in MAP's archive
LAST_YEAR = 2025              # Last year in MAP's archive (still being reported, so partial)
TOP_JUMPS = 5                 # How many of the biggest year-over-year jumps to show
SUSPICIOUS_COUNT = 5          # How many suspicious years the lab asks us to list


def load_dallas(path):
    """Read MAP's archive and return only Dallas PD's rows (filtered on ORI)."""
    df = pd.read_csv(path)
    return df[df["ORI"] == DALLAS_PD_ORI]


def build_series(dallas):
    """Group Dallas rows by year into reported, cleared and clearance (cleared / reported)."""
    per_year = dallas.groupby("YEAR").agg(
        reported=("MRD", "sum"),        # MRD = murders reported that year
        cleared=("CLR", "sum"),         # CLR = murders cleared (arrest OR exceptional means)
    )
    # MAP stores CLR as a decimal (109.0); counts are whole numbers, so make them ints
    per_year = per_year.astype({"reported": int, "cleared": int})
    per_year["clearance"] = per_year["cleared"] / per_year["reported"]
    per_year.index.name = "year"        # Lowercase, to match the deliverable's column names
    return per_year


def over_100_percent(per_year):
    """Sanity check 1: years whose clearance rate is above 100%."""
    return per_year[per_year["clearance"] > 1]


def missing_years(per_year, first=FIRST_YEAR, last=LAST_YEAR):
    """Sanity check 2: years between first and last that have no row at all."""
    return sorted(set(range(first, last + 1)) - set(per_year.index))


def biggest_jumps(per_year, n=TOP_JUMPS):
    """Sanity check 3: the n biggest year-over-year changes in clearance rate (absolute)."""
    return per_year["clearance"].diff().abs().sort_values(ascending=False).head(n)


def suspicious_years(per_year, dallas, n=SUSPICIOUS_COUNT, last=LAST_YEAR):
    """Return up to n (year, reason) pairs, most suspicious first.

    Red flags, in priority order: a rate over 100%, the partial final year,
    rows that came from MAP's FOIA requests instead of the FBI's own files,
    then the biggest year-over-year jumps in clearance.
    """
    reasons = {}                                       # year -> list of reasons
    def flag(year, why):
        reasons.setdefault(int(year), []).append(why)

    for year, row in over_100_percent(per_year).iterrows():
        flag(year, f"clearance {row['clearance']:.0%} is over 100%: prior-year cases counted as cleared this year")
    if last in per_year.index:
        flag(last, "partial year: agencies are still reporting, so counts will change")
    if "Source" in dallas.columns:
        for year in sorted(dallas.loc[dallas["Source"] != "FBI", "YEAR"].unique()):
            flag(year, "counts came from MAP's FOIA request, not from Dallas's own report to the FBI")
    change = per_year["clearance"].diff()
    for year, jump in change.abs().sort_values(ascending=False).items():
        if len(reasons) >= n and year not in reasons:
            break
        direction = "up" if change[year] > 0 else "down"
        flag(year, f"clearance {direction} {jump * 100:.0f} percentage points from the year before "
                   f"({per_year['clearance'].get(year - 1, float('nan')):.0%} -> {per_year['clearance'][year]:.0%})")
    return [(year, "; ".join(why)) for year, why in list(reasons.items())[:n]]


def main():
    """Load, inspect, build the series, run the sanity checks, and print the suspicious years."""
    df = pd.read_csv(MAP_FILE)
    print("MAP file shape:", df.shape)                 # First moves, always: shape, columns, head
    print("MAP columns:", df.columns.tolist())
    print(df.head())
    wapo = pd.read_csv(WAPO_DALLAS_FILE)
    print("\nWaPo Dallas shape:", wapo.shape)
    print("WaPo columns:", wapo.columns.tolist())

    dallas = df[df["ORI"] == DALLAS_PD_ORI]
    print(f"\nDallas PD rows: {len(dallas)}")         # Expect 61 (1965-2025)

    per_year = build_series(dallas)
    SERIES_FILE.parent.mkdir(exist_ok=True)
    per_year.to_csv(SERIES_FILE)
    print(f"wrote {SERIES_FILE.relative_to(PROJECT_ROOT)} ({len(per_year)} years)")

    print("\nSANITY CHECK 1: clearance over 100%")
    over = over_100_percent(per_year)
    print(over if len(over) else "none")
    print("\nSANITY CHECK 2: missing years")
    print(missing_years(per_year) or "none")
    print(f"\nSANITY CHECK 3: {TOP_JUMPS} biggest year-over-year jumps in clearance")
    print(biggest_jumps(per_year).round(3))

    print(f"\n{SUSPICIOUS_COUNT} MOST SUSPICIOUS YEARS")
    for year, why in suspicious_years(per_year, dallas):
        print(f"{year}: {why}")


if __name__ == "__main__":
    main()
