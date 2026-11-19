# Factor writeup — Squad Codex

## Hypothesis (as locked at standup)

We hypothesize that **Dallas PD sworn officers per homicide** is associated with Dallas homicide clearance, in the **positive** direction. We also test a **one-year lag**, because of the 2016–17 pension-driven exodus of veteran officers.

**Why this factor.** Solving a murder takes investigator hours, and most cases that get solved are solved in the first days. Fewer officers per homicide means less attention per case. Dallas had a natural shock: as the Dallas Police and Fire Pension System failed in 2016–17, veteran officers retired faster than they could be replaced. In April 2017 the department had about 3,077 officers, its lowest in a decade, down from nearly 3,700 six years earlier, and had lost 244 officers that year, many with 20+ years of experience ([Police1, 2017](https://www.police1.com/police-recruiting/articles/number-of-dallas-officers-at-lowest-level-in-a-decade-eOc4oOjmpx2l29nB/)). In 2018 our week 9 series shows clearance at **40%**, the lowest in 61 years.

## Data

- **Clearance:** `reports/dallas_series.csv` (FBI UCR via the Murder Accountability Project, ORI `TXDPD00`). FBI definition: cleared = arrest **or** exceptional means, counted in the year the clearance happens.
- **Factor:** Dallas PD sworn officers per year, from the FBI Crime Data Explorer, Law Enforcement Employees, ORI `TXDPD0000` (`cde.ucr.cjis.gov/LATEST/pe/TX/TXDPD0000`), fetched by `src/factor.py` into `data/dpd_staffing.csv`. Downloaded: **2026-11-18**. The FBI's staffing data starts in 1985 and has **no Dallas figure for 2012**.
- **Measure:** `officers_per_100_homicides = sworn_total / reported × 100`.
- **After merge:** years **1985–2025**, n = **40** (41 years minus 2012). The lag-1 model has n = 38: 1985 has no prior year, and 2013 has no 2012.
- **Anchor check** vs the supplement: 2010 = 3,666 sworn (supplement ≈3,597, within 2%), 2018 = 3,007 (matches), 2024 = 3,112 (≈3,120). The FBI series is consistent with the city's own figures.

## Result

Numbers below are copied from `reports/factor_results.txt`, written by `python -m src.factor`.

| Model | coef | p | R² | n |
|---|---|---|---|---|
| **Primary:** clearance ~ officers_per_100_homicides | −0.000055 | 0.027 | 0.122 | 40 |
| **Lag-1:** clearance ~ officers_per_100_homicides_lag1 | −0.000071 | 0.009 | 0.173 | 38 |
| Check (not the hypothesis): clearance ~ sworn_total | −0.000094 | 0.039 | 0.107 | 40 |

**In words:** the sign is the **opposite** of our hypothesis. Each additional 100 officers per 100 homicides is associated with clearance about **0.55 percentage points lower** (95% CI: −1.04 to −0.07). Across the observed range (650 officers per 100 homicides in 1988 to 3,054 in 2014) that is about 13 points. The lag-1 model points the same way and is slightly stronger (−0.71 points per 100, p = 0.009, R² = 0.17). The check model, which removes the shared denominator, also comes out negative (about −0.9 points per 100 more sworn officers). Staffing explains only 11–17% of the year-to-year variation in clearance.

**The 2016–18 pension period, described, not modeled:** sworn officers fell from 3,543 (2014) to 3,007 (2018), down 15%. Clearance went 59.6% (2015) → 49.7% (2016) → 79.6% (2017) → 39.9% (2018). The 2018 low follows the exodus, but 2017's high sits inside it, so this window alone can't separate staffing from the year-to-year shifting of clearances (confounder 2).

## Two named confounders

1. **Homicide volume (shared denominator).** Officers per homicide and clearance are both divided by the number of homicides. In a year with a homicide spike, officers per homicide falls *and* detectives are stretched across more cases, so clearance can fall even with no change in staffing. Part of any association could be the homicide count moving both numbers. The check model (`clearance ~ sworn_total`) removes the shared denominator and still comes out negative (coef −0.000094, p = 0.039), so the shared denominator is not what drives the negative sign.
2. **How the FBI counts clearances.** A clearance is counted in the year it happens, even for a murder from an earlier year. Our week 9 audit flagged 2017 (80%) followed by 2018 (40%): averaged together they come to about 60%, in line with the years around them. Clearances shifting between years, not staffing, could produce a 2018 low, and a single shock year can dominate a 61-point regression.

Also considered: **long-run trends** (Dallas's force grew for decades while clearance drifted down for reasons like case mix, so a 61-year regression can show a negative or flat association even if staffing matters in the short run; the 2016–18 shock and the lag-1 model are the sharper test), **reverse causation** (a crime wave or bad clearance year can drive hiring or departures; the lag-1 model reduces but does not remove this) and **case mix** (more stranger and gang shootings, which are harder to solve, would lower clearance with no change in staffing). The FBI counts all sworn officers, not homicide detectives, so our factor is a broad proxy for investigative capacity.

## Verdict

**Our pre-registered hypothesis is not supported.** Over **1985–2025**, Dallas PD sworn officers per homicide is **associated with lower**, not higher, homicide clearance (primary model: coef = −0.000055, p = 0.027, R² = 0.12, n = 40; lag-1: coef = −0.000071, p = 0.009, R² = 0.17, n = 38). The association is statistically significant but weak.

We do not read this as "more officers lower clearance," and we do not claim causation either way. The most likely explanation is the **long-run trend** we named before running the model: since 1985 the force grew and homicides fell, so officers per homicide rose, while clearance drifted down for reasons outside staffing, such as the shift toward harder-to-solve shootings. Two long trends moving in opposite directions produce a negative correlation on their own. A year-level, department-wide count cannot isolate the 2016–17 exodus; testing it properly would need homicide-unit staffing and detective experience by year, which DPD holds but does not publish.
