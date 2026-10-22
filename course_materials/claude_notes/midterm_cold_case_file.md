# Midterm: The Cold Case File (weeks 2–7 combined)

Deck: `ITSS3312_Midterm_Project_Cold_Case_File.pptx` (not in `slides/` yet). Due and presented Wed 10/14/2026. Grade split: code 30% + briefing 70%.

## The task
Clean `data/midterm_cases_raw.csv` (9 columns, 5,000+ rows, incidents from 1981–2025) into:
- `cases_clean.csv`, sorted by case_id, with columns `case_id,victim_name,sex,age,incident_date,year,beat,status,callback_phone`
- `quarantine.csv`, with columns `line_number,reason,raw_row`
- `report.txt`

One command runs the whole thing. **Standard library only** (csv, re, datetime).

## The cleaning standard (apply in this order)
**Quarantine the row** when a critical field is broken. Reasons:
- `wrong field count`: the row doesn't have exactly 9 fields
- `bad case_id`: can't be normalized to `CC-` + 5 digits
- `missing date`: blank, `N/A` or `unknown`
- `invalid date`: not one of the 3 formats (`2018-03-22`, `6/7/2000`, `July 1, 2022`), or impossible (Feb 30, month 13)
- `future date`: after "today", 10/07/2026
- `unknown status`: doesn't map to OPEN or CLOSED

**Repair and keep the row** when a non-critical field is messy:
- status: `OPEN`/`OPN` → OPEN; `CLOSED`/`CLSD`/`CLEARED` → CLOSED
- name: strip, collapse spaces, Title Case
- sex: M / F, anything else → U
- age: a whole number from 0 to 110, otherwise blank
- beat: the 3 digits, otherwise blank
- address: dropped from the output
- callback_phone: the first phone number in tip_notes, written `214-555-1234`, blank if there isn't one

**Duplicates:** same case_id after cleaning → keep the first, and skip (don't quarantine) the rest.

## Code requirements (by week)
- Wk 2: strings
- Wk 3: one pass with accumulators
- Wk 4: a set for dedupe and dicts for the counts
- Wk 5: one docstring-ed function per field cleaner, regex
- Wk 6: csv, try/except ValueError for quarantine, 5+ pytest tests with at least 2 failure paths
- Wk 7: a `Case` class with `from_row()`, `years_unsolved`, `is_stale`

## Our results (reports/report.txt)
- Intake: 5,112 data rows − 204 quarantined − 312 duplicates = **4,596 clean cases**. 14 blank lines and 4 header rows were skipped.
- Quarantine reasons:

  | Reason | Rows |
  |---|---|
  | wrong field count | 46 |
  | missing date | 41 |
  | bad case_id | 38 |
  | invalid date | 33 |
  | unknown status | 29 |
  | future date | 17 |

  All of the wrong-field-count rows are *truncated* (1–7 fields).
- Overall clearance: **62.2%** (2,860 closed / 1,736 open).
- By decade: 1980s 74.1%, 1990s 68.4%, 2000s 61.1%, 2010s 53.6%, 2020s 43.5%. Older cases have had more time to close, so be careful comparing decades.
- 1,504 stale open cases (5+ years). The 5 oldest open cases are all from 1981.
- Top beats by open cases: 517 (51 open, 33.8% cleared), 121 (43 open, 40.3%), 451 (39 open, 52.4%).
- 45.6% of open cases have a callback phone.
- Raw vs clean clearance: 36.2% → 62.2% (+26.1 points). The raw count only matched the exact text `CLOSED`, missing `Closed`/`CLSD`/`CLEARED`, and duplicates and junk rows inflated the denominator.

## Findings and judgment calls (verified against the data)
- **Date order:** slash dates are read as MM/DD/YYYY. 950 of the 1,520 slash dates only work month-first (for example `6/25/2000`), and 510 are ambiguous (for example `6/7/2000` on line 3, CC-76856).
- **"Stale" is measured by calendar year** (`2026 − year`). By exact date it would be 1,493 instead of 1,504.
- **Top-10 beats** clear 47.0% vs 65.3% for the other beats. Volume, recency, callback coverage and victim profile don't explain the gap: their decade mix predicts about 62%. Wording used in the briefing: "Their backlog is associated with lower clearance, not more or newer cases."
- `quarantine.csv` rebuilds `raw_row` with `",".join(row)`, so the original quote marks are lost.
