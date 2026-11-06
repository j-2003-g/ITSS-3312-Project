# intake.py
# This is the file you RUN, from the project's top folder:  python -m src.intake
# It reads data/midterm_cases_raw.csv, cleans every row using src/models.py,
# and creates three files in reports/: cases_clean.csv, quarantine.csv, and report.txt.

import csv                    # Python's built-in tool for reading and writing CSV files
from pathlib import Path      # Builds file paths that work on Windows, Mac, and Linux
from src.models import Case   # Bring in our Case class from src/models.py

# Settings (ALL CAPS = a setting that doesn't change)
# __file__ is this file (src/intake.py); .parent.parent is the project's top folder.
# Building paths from there means the script finds its files from any folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "midterm_cases_raw.csv"   # The raw file to clean
REPORTS_DIR = PROJECT_ROOT / "reports"                         # Where the 3 output files go


def main():
    """Read, clean, analyze, and save cold case records."""

    # --- Containers that fill up as we read the file ---
    cases = []                  # Store valid Case objects (a list keeps them in order)
    quarantine = []             # Store rejected rows
    seen_ids = set()            # Track duplicate case IDs (a set never holds the same value twice, and checking it is fast)
    reasons = {}                # Count quarantine reasons (a dict: reason -> how many times it happened)

    # --- Counters (called "accumulators"): each starts at 0 and goes up by 1 ---
    data_rows = 0               # Real data rows (not blank, not a header)
    blank_skipped = 0           # Empty lines we skipped
    headers_skipped = 0         # Header rows we skipped (they repeat mid-file)
    duplicates = 0              # Rows whose case_id we already had
    raw_closed = 0              # Rows whose RAW status is exactly "CLOSED" (for the raw vs clean comparison)

    # STEP 1: Read and clean the original CSV
    # "with open(...)" opens the file and closes it automatically when the block ends.
    # newline="" is what the csv module recommends so line endings are handled correctly.
    with open(INPUT_FILE, newline="") as file:
        reader = csv.reader(file)      # Turns each line into a list of values, e.g. ["CC-14731", "Mendoza, C", ...]
        # enumerate gives a counter alongside each row; start=1 so the first line is line 1
        for line_number, row in enumerate(reader, start=1):
            # Skip blank lines
            # "not row" is True for a completely empty line; all(...) is True if every value is just spaces
            if not row or all(value.strip() == "" for value in row):
                blank_skipped += 1
                continue                # "continue" jumps straight to the next row
            # Skip the original or repeated header
            if row[0].strip().lower() == "case_id":
                headers_skipped += 1
                continue
            data_rows += 1              # If we got here, this is a real data row
            # Calculate raw clearance before cleaning
            # (counts only rows with exactly "CLOSED", so "Closed", "CLSD", "CLEARED" are missed on purpose)
            if len(row) == 9 and row[7] == "CLOSED":
                raw_closed += 1
            # Try cleaning the row
            try:
                case = Case.from_row(row)          # Clean every field and build a Case object
            except ValueError as error:            # A cleaner raised an error -> this row is rejected
                reason = str(error)                # The error's message, e.g. "missing date"
                # Match the assignment's reason names
                if reason == "bad status":
                    reason = "unknown status"
                quarantine.append([                # Save the rejected row for quarantine.csv
                    line_number,                   # Where it was in the raw file
                    reason,                        # Why it was rejected
                    ",".join(row)                  # The original values glued back together with commas
                ])
                if reason not in reasons:          # First time we've seen this reason?
                    reasons[reason] = 0            # Start its count at 0
                reasons[reason] += 1               # Add 1 to this reason's count
                continue                           # Move on to the next row
            # Remove duplicate case IDs
            # The ID was already cleaned, so " CC-76856 " and "cc-76856" count as the same case
            if case.case_id in seen_ids:           # Already kept a case with this ID?
                duplicates += 1                    # Count it and skip it (we keep the FIRST copy)
                continue
            seen_ids.add(case.case_id)             # Remember this ID for later rows
            cases.append(case)                     # Keep this clean case

    # STEP 2: Sort cleaned cases by case ID
    # key=lambda ... tells sort WHAT to sort by; a lambda is a tiny one-line function
    cases.sort(key=lambda case: case.case_id)

    # STEP 3: Save cases_clean.csv
    REPORTS_DIR.mkdir(exist_ok=True)                         # Make sure reports/ exists (no error if it already does)
    with open(REPORTS_DIR / "cases_clean.csv", "w", newline="") as file:   # "w" = write (creates or overwrites the file)
        writer = csv.writer(file)                            # Turns lists into CSV lines (adds quotes where needed)
        writer.writerow([                                    # First line: the column headers
            "case_id", "victim_name", "sex", "age",
            "incident_date", "year", "beat", "status",
            "callback_phone"
        ])
        for case in cases:                                   # One line per clean case
            writer.writerow(case.to_row())                   # to_row() gives the values in the same order as the headers

    # STEP 4: Save quarantine.csv
    with open(REPORTS_DIR / "quarantine.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["line_number", "reason", "raw_row"])   # Header line
        for row in quarantine:                                  # One line per rejected row
            writer.writerow(row)

    # STEP 5: Prepare statistics
    closed_count = 0            # How many clean cases are CLOSED
    open_cases = []             # List of the OPEN cases (we need them later for "oldest open")
    stale_count = 0             # OPEN cases unsolved for 5+ years
    callback_count = 0          # OPEN cases that have a callback phone number

    decades = {}                # e.g. {1980: {"total": 916, "closed": 679}, ...}
    beats = {}                  # e.g. {"517": {"total": 77, "closed": 26, "open": 51}, ...}

    for case in cases:          # One pass over every clean case
        # Overall status counts
        if case.status == "CLOSED":
            closed_count += 1
        else:                                    # Otherwise the case is OPEN
            open_cases.append(case)
            if case.is_stale:                    # is_stale is a property on the Case class
                stale_count += 1
            if case.callback_phone != "":        # Not blank -> the tips contain a phone number
                callback_count += 1
        # Count cases by decade
        # "//" divides and drops the remainder: 1994 // 10 = 199, then * 10 = 1990
        decade = (case.year // 10) * 10
        if decade not in decades:                # First case from this decade? Create its counters
            decades[decade] = {"total": 0, "closed": 0}
        decades[decade]["total"] += 1
        if case.status == "CLOSED":
            decades[decade]["closed"] += 1
        # Count cases by police beat
        if case.beat != "":                      # Skip cases with no beat (blank)

            if case.beat not in beats:           # First case from this beat? Create its counters
                beats[case.beat] = {
                    "total": 0,
                    "closed": 0,
                    "open": 0
                }

            beats[case.beat]["total"] += 1

            if case.status == "CLOSED":
                beats[case.beat]["closed"] += 1
            else:
                beats[case.beat]["open"] += 1

    # STEP 6: Calculate percentages
    clean_count = len(cases)          # len() = how many items are in the list
    open_count = len(open_cases)

    clean_rate = 0                    # Start at 0 in case there's nothing to divide by
    raw_rate = 0
    callback_rate = 0

    # Each "if ... > 0" protects against dividing by zero, which would crash
    if clean_count > 0:
        clean_rate = closed_count / clean_count * 100       # Clearance rate after cleaning, as a percent

    if data_rows > 0:
        raw_rate = raw_closed / data_rows * 100             # "Face value" clearance rate before cleaning

    if open_count > 0:
        callback_rate = callback_count / open_count * 100   # % of OPEN cases with a phone lead

    # STEP 7: Create report
    # We build the report as a list of text lines, then print and save it in Step 8.
    # f"..." strings (f-strings) put variable values inside {curly braces}.
    # "\n" at the start of a line adds an empty line before it.
    report = []
    report.append("THE COLD CASE FILE - CLEANING REPORT")
    report.append("===================================")

    # Section 1: what happened to every row of the raw file
    report.append("\n1. INTAKE SUMMARY")
    report.append(f"Data rows read: {data_rows}")
    report.append(f"Blank lines skipped: {blank_skipped}")
    report.append(f"Header rows skipped: {headers_skipped}")
    report.append(f"Quarantined rows: {len(quarantine)}")
    report.append(f"Duplicates removed: {duplicates}")
    report.append(f"Clean cases: {clean_count}")
    report.append("\nQuarantine reasons:")
    for reason in sorted(reasons):                     # sorted() lists the reasons alphabetically
        report.append(f"{reason}: {reasons[reason]}")  # e.g. "missing date: 41"

    # Section 2: overall clearance
    report.append("\n2. OVERALL CLEARANCE RATE")
    report.append(f"Closed cases: {closed_count}")
    report.append(f"Open cases: {open_count}")
    report.append(f"Clearance rate: {clean_rate:.1f}%")   # :.1f = show 1 digit after the decimal point

    # Section 3: clearance for each decade
    report.append("\n3. CLEARANCE RATE BY DECADE")
    for decade in range(1980, 2030, 10):    # 1980, 1990, 2000, 2010, 2020 (2030 itself is not included)
        total = 0                           # Default to 0 in case a decade has no cases
        closed = 0
        if decade in decades:
            total = decades[decade]["total"]
            closed = decades[decade]["closed"]
        rate = 0
        if total > 0:                       # Avoid dividing by zero
            rate = closed / total * 100
        report.append(
            f"{decade}s: {closed}/{total} closed ({rate:.1f}%)"   # e.g. "1980s: 679/916 closed (74.1%)"
        )

    # Section 4: stale and oldest open cases
    report.append("\n4. STALE AND OLDEST OPEN CASES")
    report.append(f"Stale OPEN cases (5+ years): {stale_count}")
    # Oldest cases have the earliest incident dates
    # (dates are "YYYY-MM-DD" text, so sorting them alphabetically also sorts them by time)
    open_cases.sort(key=lambda case: case.incident_date)
    report.append("\nFive oldest OPEN cases:")
    for case in open_cases[:5]:             # [:5] = the first 5 items of the list
        report.append(
            f"{case.case_id} | {case.victim_name} | "
            f"{case.incident_date} | {case.years_unsolved} years"
        )

    # Section 5: beats with the most open cases
    report.append("\n5. TOP 10 BEATS BY OPEN CASES")
    # Sort beats by number of OPEN cases, highest first
    # The minus sign flips the order so the biggest open count comes first.
    # If two beats tie, the beat number decides (lowest first).
    top_beats = sorted(
        beats,
        key=lambda beat: (-beats[beat]["open"], beat)
    )
    for beat in top_beats[:10]:             # Only the first 10 beats
        total = beats[beat]["total"]
        closed = beats[beat]["closed"]
        opened = beats[beat]["open"]

        rate = 0

        if total > 0:
            rate = closed / total * 100     # This beat's clearance rate

        report.append(
            f"Beat {beat}: {opened} OPEN | "
            f"Clearance rate: {rate:.1f}%"
        )

    # Section 6: how many open cases have a phone lead
    report.append("\n6. CALLBACK PHONE COVERAGE")
    report.append(f"OPEN cases with callback: {callback_count}")
    report.append(f"Callback coverage: {callback_rate:.1f}%")

    # Section 7: how much the cleaning changed the answer
    report.append("\n7. RAW VS CLEAN CLEARANCE RATE")
    report.append(f"Raw clearance rate: {raw_rate:.1f}%")
    report.append(f"Clean clearance rate: {clean_rate:.1f}%")
    report.append(
        f"Difference: {clean_rate - raw_rate:+.1f} percentage points"   # :+.1f always shows a + or - sign
    )

    # STEP 8: Print and save the report
    with open(REPORTS_DIR / "report.txt", "w") as file:

        for line in report:
            print(line)                     # Show the line in the terminal
            file.write(line + "\n")         # Save the line to report.txt ("\n" ends the line)

    print("\nFinished creating all three output files!")


# This line means: only run main() when this file is run directly
# (python -m src.intake), NOT when another file imports it.
if __name__ == "__main__":
    main()
