# Week 8: The Pro Workflow (branching, PR reviews, packages, venv)

Deck: `slides/08-ITSS-OPRE3312-Pro_Workflow_Branching_Packages.pptx`. First week of the second half; the answer repo is closed from here on.

## Branching strategy
- **We run trunk-based development:** tiny `feature/wkN-task` branches, merged within the week.
- Other strategies: long-lived feature branches (drift), release branches (we'll cut one in **week 15** for the deployed app), and "everyone on main" (chaos; never do it).
- Having one strategy that everyone follows matters more than which one.

## The reviewer's checklist (in this order)
1. Does it **run**? Pull the branch and run it.
2. Do the **tests pass**? `pytest` is not optional.
3. Can the author **explain every line**?
4. **Names:** would a stranger understand them?
5. Any **bare `except`**? Any **magic numbers**?
6. Does it do **one thing**?
7. Then, and only then: style nits.

## Package layout (slide 6)
```
README.md, requirements.txt
data/       raw inputs (gitignored if big)
src/        __init__.py, intake.py, models.py (Case), patterns.py (regex extractors)
tests/      test_intake.py
reports/    outputs and charts (week 10+)
```

## venv + requirements.txt
```
python -m venv .venv
.venv\Scripts\activate            (Windows)
source .venv/bin/activate         (Mac/Linux)
pip install pytest pandas
pip freeze > requirements.txt     # the lockfile: commit it
pip install -r requirements.txt   # how a teammate or a server rebuilds the env
```
`.venv` goes in `.gitignore`.

## Lab: Operation Renovation (branch `feature/wk8-renovation`)
1. Create the skeleton folders: `src/`, `tests/`, `data/`, `reports/`.
2. `git mv` the modules into `src/`. `git mv` preserves history.
3. Fix the imports (`from src.intake import ...`) and add `__init__.py`. Run pytest until it's green.
4. Create the venv, `pip install pytest`, `pip freeze > requirements.txt`, and gitignore `.venv`.
5. Open a PR. The **next squad** reviews it with the checklist (1→2→3→4→1); address the comments, then merge.

**Done means:**
- The tree matches slide 6.
- `pytest` is green, importing from `src/`.
- `requirements.txt` is committed and `.venv` is ignored.
- The PR has **at least 2 review comments from another squad**, and they've been addressed.
- Our squad left **at least 2 substantive comments** on the squad we reviewed.

## How we did it (feature/wk8-renovation/try220000)
- Merged the midterm code into `main`'s history, then `git mv`-ed it into the new layout:
  - `case_model.py` → `src/models.py`
  - `clean_cases.py` → `src/intake.py`
  - `test_cases.py` → `tests/test_intake.py`
  - the raw CSV → `data/`
  - the outputs → `reports/`
- Moved the field cleaners into `src/patterns.py`, leaving `Case` in `models.py`. The function bodies are unchanged.
- `src/intake.py` builds its paths from the project root, so `python -m src.intake` reads `data/` and writes `reports/`.
- `pytest.ini` sets `pythonpath = .` so a plain `pytest` works from the top folder.

## Next week
`pip install pandas requests` (then re-freeze). Run the week 9 downloads before class. The real data arrives: MAP's homicide archive and the Washington Post's Dallas file.
