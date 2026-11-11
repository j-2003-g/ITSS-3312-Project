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
│   └─ patterns.py      # field cleaners / regex extractors (case_id, date, phone, ...)
├─ tests/
│   └─ test_intake.py   # pytest tests for the cleaners
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

## Run it

From the project's top folder, with the venv activated:

```bash
python -m src.intake    # writes reports/cases_clean.csv, reports/quarantine.csv, reports/report.txt
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
