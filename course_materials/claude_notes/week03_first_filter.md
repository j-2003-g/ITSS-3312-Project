# Week 3: The First Filter (conditionals, loops, accumulators)

Deck: `slides/03-ITSS-OPRE3312-The_First_Filter_Conditionals_Loops.pptx`

## Concepts taught
- **`if / elif / else` flagging:** Python takes the *first* true branch, so put the most specific condition first. Combine conditions with `and` / `or` / `not`.
  ```python
  years_unsolved = 2026 - year
  if years_unsolved >= 5:   flag = "*** STALE ***"
  elif years_unsolved >= 2: flag = "aging"
  else:                     flag = "recent"
  ```
- **Comparisons are case-sensitive** (`'open' == 'OPEN'` is False). That's why values get standardized first (week 2).
- **`for` loops:** one block of code for every record ("3 records or 3 million: same 4 lines").
- **The accumulator pattern:** set up the counter *before* the loop, update it *inside*, report *after*. Setting it up inside the loop by accident resets the count on every record.
- **Loop control:** `continue` skips blank or junk lines ("your bouncer at the door"); `break` stops the loop entirely. A loop should shrug off odd lines, not crash.

## Lab: `first_filter.py` (branch `feature/wk3-filter`)
- Input: `wk03_data_raw_cases_50.txt`, 50 pipe-delimited (`|`) records with blank-ish lines planted.
- Steps: parse every record → flag `*** STALE ***` for open cases 5+ years old → count juvenile victims (age < 18) among OPEN cases → report the counts.
- Required output:
  ```
  Total records:        50
  Open cases:           29
  Stale (>= 5 yrs):     27
  Oldest open case:     Fuentes, Lamar (1980)
  ```
- Done means: merged via a reviewed PR, zero crashes on the full file, all four counts correct, and at least one commit from every squad member.

## Why it matters later
The per-beat counts become the low-arrest-zone map in week 10.
