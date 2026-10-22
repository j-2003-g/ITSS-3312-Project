# Week 4: Evidence Lockers (lists, sets, dicts)

Deck: `slides/04-ITSS-OPRE3312-Evidence_Lockers_Lists_Sets_Dicts.pptx`

## Concepts taught
- **list → order.** `append` to collect, then `len`, `min`, `max`, `sum / len`, `sorted(...)[0:5]`. Collect first, analyze afterwards.
- **set → unique.** The dedupe machine. Rule of the unit: **never count anything until you've deduped it, and never dedupe until you've normalized it** (`strip().upper()` first).
- **dict → labeled.** Count anything by anything. This is *the* counting pattern:
  ```python
  if key in counts: counts[key] += 1
  else:             counts[key] = 1
  ```
- **Ranking a dict:** `sorted(per_beat, key=per_beat.get, reverse=True)`, with `"#" * count` as a text bar chart.
- **Pick the right container:** the right one takes one line; the wrong one costs an evening (for example, a nested loop to dedupe).

## Lab: `lockers.py` (branch `feature/wk4-lockers`)
- Input: `wk04_data_raw_cases_dupes.txt`, 60 lines with duplicates in different formatting.
- Order: normalize → dedupe → collect → count → rank.
- Required output:
  ```
  Lines in file:      60
  Unique records:     52
  Duplicates removed: 8
  Youngest 17 / Oldest 70 / Average 39.1
  Beat ranking, most open cases first, with # bars
  ```
- The reviewer must check that dedupe happens *after* normalization, that age stats use unique records only, and that the ranking is descending.

## Why it matters later
The solve rate per victim group is a dict, and the beat ranking becomes the week 10 map. Duplicates inflate real crime statistics, which is week 9's first real headache.

## Next (week 5)
Wrap the intake pipeline in `def parse_record()`, then use regex to pull phones, dates and case numbers out of free-text tip notes.
