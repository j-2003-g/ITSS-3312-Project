# get_data.py
# Downloads the two week 9 datasets into data/, straight from the publishers.
# Run it from the project's top folder:   python -m src.get_data
# Anyone who clones the repo runs this once and gets the same data/ folder,
# so the big raw files never have to be committed to Git.

from pathlib import Path      # Builds file paths that work on Windows, Mac, and Linux
import pandas as pd           # Reads and filters the Washington Post file
import requests               # Downloads files over HTTPS

# Settings (ALL CAPS = a value that doesn't change)
PROJECT_ROOT = Path(__file__).resolve().parent.parent   # The project's top folder
DATA_DIR = PROJECT_ROOT / "data"

# MAP's FBI homicide archive (Dropbox link from murderdata.org/p/data-docs.html).
# Dropbox links can rotate: if this returns a web page instead of a CSV, copy
# the current CSV link from that page.
MAP_URL = ("https://www.dropbox.com/scl/fi/4y2a6yy0pv4lxffm7sa4v/UCR65_25.csv"
           "?rlkey=jhs7ktqhb9h3dnml1wety4nhb&st=7rxppnar&dl=1")
# The Washington Post's case-level file (all 50 cities)
WAPO_URL = ("https://raw.githubusercontent.com/washingtonpost/"
            "data-homicides/master/homicide-data.csv")

MAP_FILE = DATA_DIR / "map_ucr.csv"
WAPO_ALL_FILE = DATA_DIR / "wapo_all.csv"
WAPO_DALLAS_FILE = DATA_DIR / "wapo_dallas.csv"
EXPECTED_WAPO_DALLAS_ROWS = 1567          # The handout says we must get exactly this many
NAME_COLUMNS = ["victim_last", "victim_first"]   # Real victims' names: dropped, never saved or printed
DOWNLOAD_TIMEOUT_SECONDS = 120


def fetch(url, dest):
    """Download url to dest, unless dest already exists (then reuse the cached copy)."""
    if dest.exists():
        print(f"cached: {dest.name}")
        return
    response = requests.get(url, timeout=DOWNLOAD_TIMEOUT_SECONDS)
    response.raise_for_status()                  # Stop with an error on a 404/403 instead of saving an error page
    if response.content.lstrip()[:15].lower().startswith(b"<!doctype html"):
        raise ValueError(f"{url} returned a web page, not a CSV. The link may have rotated.")
    dest.write_bytes(response.content)
    print(f"saved: {dest.name} ({dest.stat().st_size:,} bytes)")


def build_wapo_dallas(all_file, dallas_file):
    """Keep only Dallas rows from the Post's national file, drop the name columns, save, and return the row count."""
    # The Post's file is Latin-1, not UTF-8; without this pandas raises UnicodeDecodeError
    wapo = pd.read_csv(all_file, encoding="latin-1")
    dallas = wapo[wapo["city"] == "Dallas"].drop(columns=NAME_COLUMNS)   # Filter on city, not state
    dallas.to_csv(dallas_file, index=False)
    return len(dallas)


def main():
    """Download both sources and build data/wapo_dallas.csv."""
    DATA_DIR.mkdir(exist_ok=True)
    fetch(MAP_URL, MAP_FILE)
    fetch(WAPO_URL, WAPO_ALL_FILE)
    rows = build_wapo_dallas(WAPO_ALL_FILE, WAPO_DALLAS_FILE)
    print(f"wapo_dallas.csv: {rows} rows (expect {EXPECTED_WAPO_DALLAS_ROWS})")


if __name__ == "__main__":     # Run main() only when this file is run directly
    main()
