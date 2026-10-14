import csv
from case_model import Case

INPUT_FILE = "midterm_cases_raw.csv"

def main():
    """Read, clean, analyze, and save cold case records."""

    cases = []                  # Store valid Case objects
    quarantine = []             # Store rejected rows
    seen_ids = set()            # Track duplicate case IDs
    reasons = {}                # Count quarantine reasons

    data_rows = 0
    blank_skipped = 0
    headers_skipped = 0
    duplicates = 0
    raw_closed = 0

    # STEP 1: Read and clean the original CSV
    with open(INPUT_FILE, newline="") as file:
        reader = csv.reader(file)
        for line_number, row in enumerate(reader, start=1):
            # Skip blank lines
            if not row or all(value.strip() == "" for value in row):
                blank_skipped += 1
                continue
            # Skip the original or repeated header
            if row[0].strip().lower() == "case_id":
                headers_skipped += 1
                continue
            data_rows += 1
            # Calculate raw clearance before cleaning
            if len(row) == 9 and row[7] == "CLOSED":
                raw_closed += 1
            # Try cleaning the row
            try:
                case = Case.from_row(row)
            except ValueError as error:
                reason = str(error)
                # Match the assignment's reason names
                if reason == "bad status":
                    reason = "unknown status"
                quarantine.append([
                    line_number,
                    reason,
                    ",".join(row)
                ])
                if reason not in reasons:
                    reasons[reason] = 0
                reasons[reason] += 1
                continue
            # Remove duplicate case IDs
            if case.case_id in seen_ids:
                duplicates += 1
                continue
            seen_ids.add(case.case_id)
            cases.append(case)
    # STEP 2: Sort cleaned cases by case ID
    cases.sort(key=lambda case: case.case_id)
    # STEP 3: Save cases_clean.csv
    with open("cases_clean.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "case_id", "victim_name", "sex", "age",
            "incident_date", "year", "beat", "status",
            "callback_phone"
        ])
        for case in cases:
            writer.writerow(case.to_row())
    # STEP 4: Save quarantine.csv
    with open("quarantine.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["line_number", "reason", "raw_row"])
        for row in quarantine:
            writer.writerow(row)
    # STEP 5: Prepare statistics
    closed_count = 0
    open_cases = []
    stale_count = 0
    callback_count = 0

    decades = {}
    beats = {}

    for case in cases:
        # Overall status counts
        if case.status == "CLOSED":
            closed_count += 1
        else:
            open_cases.append(case)
            if case.is_stale:
                stale_count += 1
            if case.callback_phone != "":
                callback_count += 1
        # Count cases by decade
        decade = (case.year // 10) * 10
        if decade not in decades:
            decades[decade] = {"total": 0, "closed": 0}
        decades[decade]["total"] += 1
        if case.status == "CLOSED":
            decades[decade]["closed"] += 1
        # Count cases by police beat
        if case.beat != "":

            if case.beat not in beats:
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
    clean_count = len(cases)
    open_count = len(open_cases)

    clean_rate = 0
    raw_rate = 0
    callback_rate = 0

    if clean_count > 0:
        clean_rate = closed_count / clean_count * 100

    if data_rows > 0:
        raw_rate = raw_closed / data_rows * 100

    if open_count > 0:
        callback_rate = callback_count / open_count * 100

    # STEP 7: Create report
    report = []
    report.append("THE COLD CASE FILE - CLEANING REPORT")
    report.append("===================================")
    report.append("\n1. INTAKE SUMMARY")
    report.append(f"Data rows read: {data_rows}")
    report.append(f"Blank lines skipped: {blank_skipped}")
    report.append(f"Header rows skipped: {headers_skipped}")
    report.append(f"Quarantined rows: {len(quarantine)}")
    report.append(f"Duplicates removed: {duplicates}")
    report.append(f"Clean cases: {clean_count}")
    report.append("\nQuarantine reasons:")
    for reason in sorted(reasons):
        report.append(f"{reason}: {reasons[reason]}")
    report.append("\n2. OVERALL CLEARANCE RATE")
    report.append(f"Closed cases: {closed_count}")
    report.append(f"Open cases: {open_count}")
    report.append(f"Clearance rate: {clean_rate:.1f}%")
    report.append("\n3. CLEARANCE RATE BY DECADE")
    for decade in range(1980, 2030, 10):
        total = 0
        closed = 0
        if decade in decades:
            total = decades[decade]["total"]
            closed = decades[decade]["closed"]
        rate = 0
        if total > 0:
            rate = closed / total * 100
        report.append(
            f"{decade}s: {closed}/{total} closed ({rate:.1f}%)"
        )
    report.append("\n4. STALE AND OLDEST OPEN CASES")
    report.append(f"Stale OPEN cases (5+ years): {stale_count}")
    # Oldest cases have the earliest incident dates
    open_cases.sort(key=lambda case: case.incident_date)
    report.append("\nFive oldest OPEN cases:")
    for case in open_cases[:5]:
        report.append(
            f"{case.case_id} | {case.victim_name} | "
            f"{case.incident_date} | {case.years_unsolved} years"
        )
    report.append("\n5. TOP 10 BEATS BY OPEN CASES")
    # Sort beats by number of OPEN cases, highest first
    top_beats = sorted(
        beats,
        key=lambda beat: (-beats[beat]["open"], beat)
    )
    for beat in top_beats[:10]:
        total = beats[beat]["total"]
        closed = beats[beat]["closed"]
        opened = beats[beat]["open"]
    
        rate = 0

        if total > 0:
            rate = closed / total * 100

        report.append(
            f"Beat {beat}: {opened} OPEN | "
            f"Clearance rate: {rate:.1f}%"
        )

    report.append("\n6. CALLBACK PHONE COVERAGE")
    report.append(f"OPEN cases with callback: {callback_count}")
    report.append(f"Callback coverage: {callback_rate:.1f}%")

    report.append("\n7. RAW VS CLEAN CLEARANCE RATE")
    report.append(f"Raw clearance rate: {raw_rate:.1f}%")
    report.append(f"Clean clearance rate: {clean_rate:.1f}%")
    report.append(
        f"Difference: {clean_rate - raw_rate:+.1f} percentage points"
    )
    # STEP 8: Print and save the report
    with open("report.txt", "w") as file:

        for line in report:
            print(line)
            file.write(line + "\n")

    print("\nFinished creating all three output files!")
if __name__ == "__main__":
    main()