# Project context (read this first)

## The course
- **ITSS/OPRE 3312, Fall 2026.** Students work in squads of 4 on one shared GitHub repo: `j-2003-g/ITSS-3312-Project`.
- **Theme:** an audit of Dallas homicide cold cases. Each week adds one skill, applied to case data.
- **Weekly grading:** "This week's score = this merged code on GitHub." Work only counts once it's merged to `main` through a reviewed PR.

## Semester roadmap
| Weeks | Phase | What happens |
|---|---|---|
| 1–7 | Review, re-armed | strings → loops → containers → functions/regex → files/exceptions/pytest → classes |
| 7 | Midterm | "The Cold Case File": clean 5,000+ messy rows and brief the class (see `midterm_cold_case_file.md`) |
| 8 | New material | Pro workflow: branching, PR reviews, package layout, venv (see `week08_pro_workflow.md`) |
| 9 | New material | **pandas** moves in. Real data arrives: MAP's homicide archive and the Washington Post's Dallas file |
| 10 | New material | Beat rankings become a real map of Dallas; charts go in `reports/` |
| 13–finals | Ship it live | Week 15: cut a release branch and deploy this repo as an app on a server (Linode) |

## House rules (these apply to Claude too)
- **Every squad member must be able to explain every line** of committed code; any member may be asked to in Q&A. Write code a learning student can follow, and comment non-obvious lines.
- **During labs, "ask Claude to explain (not solve)"** when a student is stuck for more than 5 minutes. If the user is in a timed lab and asks about an error, explain the cause. Only write the fix if they ask for it.
- **Midterm code was standard library only** (csv, re, datetime; no pandas). pandas is allowed from week 9.
- **The review phase had an answer repo; the second half does not.** From week 8 on, the traps in the data are real, and finding them is the audit.
- When describing findings, say "associated with", never "caused by".

## Git workflow
- **Never commit straight to `main`.** Use short-lived branches named `feature/wkN-task/<netid>` (for example `feature/wk8-renovation/try220000`), then push and open a PR.
- **PRs are reviewed by another squad** (1→2→3→4→1) using the checklist in `week08_pro_workflow.md`, then merged.
- **One thing per PR.**
- The GitHub CLI (`gh`) is not installed on this machine. Push the branch and give the user the compare link to open the PR.

## Repo layout (after the week 8 renovation)
```
src/intake.py      pipeline: python -m src.intake  (data/ in, reports/ out)
src/models.py      Case class
src/patterns.py    field cleaners / regex extractors
tests/             pytest: run `pytest` from the top folder
data/              raw inputs
reports/           outputs
requirements.txt   rebuild the venv with: pip install -r requirements.txt
```
Use the venv (`.venv\Scripts\activate` on Windows). If you add a package, re-run `pip freeze > requirements.txt` and commit it.

## Notes index
- [week03_first_filter.md](week03_first_filter.md): conditionals, loops, accumulators
- [week04_evidence_lockers.md](week04_evidence_lockers.md): lists, sets, dicts
- [midterm_cold_case_file.md](midterm_cold_case_file.md): the cleaning standard and our results
- [week08_pro_workflow.md](week08_pro_workflow.md): branching, PR reviews, package layout, venv
