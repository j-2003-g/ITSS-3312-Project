# ITSS/OPRE 3312 Squad Project: The Cold Case File

A Python package that cleans 45 years of messy police cold-case records and reports what the clean data says: clearance rates, stale cases, hardest-hit beats and callback leads.

## Project layout

```
ITSS-3312-Project/
├─ README.md
├─ requirements.txt     # exact package versions (rebuild the venv from this)
├─ pytest.ini           # lets plain `pytest` find src/ and tests/
├─ data/
│   └─ midterm_cases_raw.csv   # raw input: 5,000+ messy rows
├─ src/
│   ├─ __init__.py
│   ├─ intake.py        # the pipeline: read → clean → quarantine → dedupe → report
│   ├─ models.py        # the Case class (from_row, years_unsolved, is_stale)
│   ├─ patterns.py      # field cleaners / regex extractors (case_id, date, phone, ...)
│   ├─ get_data.py      # wk9: downloads MAP + Washington Post data into data/
│   ├─ series.py        # wk9: builds reports/dallas_series.csv + sanity checks
│   ├─ charts.py        # wk10: reports/clearance_trend.png
│   ├─ casemap.py       # wk10: reports/dallas_map.html
│   ├─ fetch_city.py    # wk11: Dallas OpenData murder incidents → data/case.db (cached)
│   └─ queries.py       # wk11: three SQL questions + city-vs-FBI comparison
├─ tests/
│   └─ test_*.py        # pytest tests, one file per module
└─ reports/             # outputs: cases_clean.csv, quarantine.csv, report.txt
```

## Setup (once per computer)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
```

`.venv/` is gitignored. Everyone rebuilds it from `requirements.txt`. If you add a package, run `pip freeze > requirements.txt` and commit the file.

Week 11 needs your own free Dallas OpenData app token (dallasopendata.com → My Profile → Developer Settings → Create New App Token). Put it in a file called `.env` at the repo root:

```
DALLAS_APP_TOKEN=paste_your_token_here
```

`.env` is gitignored. Never commit the token.

## Run it

From the project's top folder, with the venv activated:

```bash
python -m src.intake    # writes reports/cases_clean.csv, reports/quarantine.csv, reports/report.txt
python -m src.get_data  # wk9: downloads data/map_ucr.csv and data/wapo_dallas.csv (gitignored)
python -m src.series    # wk9: writes reports/dallas_series.csv, prints sanity checks
python -m src.charts    # wk10: writes reports/clearance_trend.png
python -m src.casemap   # wk10: writes reports/dallas_map.html
python -m src.fetch_city  # wk11: fetches once into data/raw_incidents.json, builds data/case.db
python -m src.queries   # wk11: murders per year, top 5 beats, our slice, city vs FBI
pytest                  # runs every test in tests/
```

## How we work

- **Branches:** short-lived feature branches named `feature/wkN-task/<netid>`, never commits straight to `main`.
- **Pull requests:** every merge to `main` goes through a reviewed PR.
- **Reviewer's checklist (in this order):**
  1. Does it run? Pull the branch and run it.
  2. Do the tests pass? Run `pytest`.
  3. Can the author explain every line?
  4. Names: would a stranger understand them?
  5. Any bare `except`? Any magic numbers?
  6. Does it do one thing?
  7. Then, and only then: style nits.

## Roadmap (weeks 8-16)

Every week adds one module to `src/` and one file to `reports/`. The full plan is in
[`course_materials/01_build_roadmap_wk08-16.md`](course_materials/01_build_roadmap_wk08-16.md).

## Data sources

- Murder Accountability Project, UCR homicide and clearance data (UCR65_25), murderdata.org.
- The Washington Post, Unsolved Homicide Database, github.com/washingtonpost/data-homicides, 2018 (CC BY-NC-SA 4.0).
- City of Dallas OpenData, Police Incidents (resource qv6i-rri7), dallasopendata.com. Published for research; DPD's Crime Analytics Dashboard is the authoritative source.

Aggregate analysis only: these files describe real victims. No names in any output, chart or commit.
