# Factor writeup — Squad Codex

## Hypothesis (as locked at standup)

We hypothesize that **Dallas PD sworn officers per homicide** is associated with Dallas homicide clearance, in the **positive** direction. We also test a **one-year lag**, because of the 2016–17 pension-driven exodus of veteran officers.

**Why this factor.** Solving a murder takes investigator hours, and most cases that get solved are solved in the first days. Fewer officers per homicide means less attention per case. Dallas had a natural shock: as the Dallas Police and Fire Pension System failed in 2016–17, veteran officers retired faster than they could be replaced. In April 2017 the department had about 3,077 officers, its lowest in a decade, down from nearly 3,700 six years earlier, and had lost 244 officers that year, many with 20+ years of experience ([Police1, 2017](https://www.police1.com/police-recruiting/articles/number-of-dallas-officers-at-lowest-level-in-a-decade-eOc4oOjmpx2l29nB/)). In 2018 our week 9 series shows clearance at **40%**, the lowest in 61 years.

## Data

- **Clearance:** `reports/dallas_series.csv` (FBI UCR via the Murder Accountability Project, ORI `TXDPD00`). FBI definition: cleared = arrest **or** exceptional means, counted in the year the clearance happens.
- **Factor:** Dallas PD sworn officers per year, from the FBI Crime Data Explorer, Law Enforcement Employees, ORI `TXDPD0000` (`cde.ucr.cjis.gov/LATEST/pe/TX/TXDPD0000`), fetched by `src/factor.py` into `data/dpd_staffing.csv`. Downloaded: **[date]**.
- **Measure:** `officers_per_100_homicides = sworn_total / reported × 100`.
- **After merge:** years **[____–____]**, n = **[__]**. Anchor check vs the supplement (≈3,597 in 2010, ≈3,007 in 2018, ≈3,120 in 2024): **[OK / differences]**.

## Result

Numbers below are copied from `reports/factor_results.txt`, written by `python -m src.factor`.

| Model | coef | p | R² | n |
|---|---|---|---|---|
| **Primary:** clearance ~ officers_per_100_homicides | [__] | [__] | [__] | [__] |
| **Lag-1:** clearance ~ officers_per_100_homicides_lag1 | [__] | [__] | [__] | [__] |
| Check (not the hypothesis): clearance ~ sworn_total | [__] | [__] | [__] | [__] |

**In words:** each additional officer per 100 homicides is associated with a [__]-point change in clearance. [One sentence: does the lag strengthen, hold, or weaken the story?]

## Two named confounders

1. **Homicide volume (shared denominator).** Officers per homicide and clearance are both divided by the number of homicides. In a year with a homicide spike, officers per homicide falls *and* detectives are stretched across more cases, so clearance can fall even with no change in staffing. Part of any association could be the homicide count moving both numbers. The check model (`clearance ~ sworn_total`) removes the shared denominator: [what it showed].
2. **How the FBI counts clearances.** A clearance is counted in the year it happens, even for a murder from an earlier year. Our week 9 audit flagged 2017 (80%) followed by 2018 (40%): averaged together they come to about 60%, in line with the years around them. Clearances shifting between years, not staffing, could produce a 2018 low, and a single shock year can dominate a 61-point regression.

Also considered: **reverse causation** (a crime wave or bad clearance year can drive hiring or departures; the lag-1 model reduces but does not remove this) and **case mix** (more stranger and gang shootings, which are harder to solve, would lower clearance with no change in staffing). The FBI counts all sworn officers, not homicide detectives, so our factor is a broad proxy for investigative capacity.

## Verdict

Over **[____–____]**, Dallas PD sworn officers per homicide is **[associated with / not detectably associated with]** Dallas homicide clearance (primary model: coef = [__], p = [__], R² = [__]). We do not claim causation, because homicide volume moves both numbers, clearances can be credited to a later year than the murder, and staffing and clearance can both respond to the same crime waves.
