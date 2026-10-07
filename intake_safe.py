# intake_safe.py - Week 6: Bulletproof Intake
# Load 100 case rows from a real CSV file. Rows that are damaged get
# QUARANTINED (logged with a line number + reason) instead of crashing
# the program. Then report how many loaded and how many were rejected.
#
# Each row has 8 fields:
#   [0] case_id  [1] victim_name  [2] sex  [3] age
#   [4] date     [5] address      [6] beat [7] status

import csv    # Python's built-in module for reading comma-separated files


DATA_FILE = "wk06_data_raw_cases_100.csv"    # the file this lab loads
EXPECTED_FIELDS = 8                          # every good row has exactly 8 fields


# ---------------------------------------------------------------
# STEP 1: parse_row() - one row in, one clean dict out (or an error)
# ---------------------------------------------------------------
# This function never prints and never catches anything. If the row
# is bad, it RAISES a ValueError that explains why, and lets the
# caller decide what to do. That keeps it small and easy to test.

def parse_row(row):
    """Turn one CSV row (a list of 8 strings) into a clean case dict, or raise ValueError."""
    if len(row) != EXPECTED_FIELDS:                     # truncated row: some fields are missing
        raise ValueError(f"expected {EXPECTED_FIELDS} fields, got {len(row)}")   # stop here with a reason

    age = int(row[3].strip())                           # text -> number; 'unknown' makes int() raise ValueError by itself

    if row[4].strip() == "":                            # an empty date field
        raise ValueError("missing date")                # stop here with a reason

    # Every check passed: build and return the clean record.
    # A dict lets us look fields up by NAME (case["age"]) instead of by position.
    return {
        "case_id": row[0].strip(),                      # "CC-20001"
        "name": row[1].strip().title(),                 # " carter, d " -> "Carter, D"
        "sex": row[2].strip().upper(),                  # "m" -> "M"
        "age": age,                                     # already converted to an int above
        "date": row[4].strip(),                         # "2018-03-22"
        "address": row[5].strip().title(),              # "412 Larkmoor"
        "beat": row[6].strip(),                         # "352"
        "status": row[7].strip().upper(),               # "open" -> "OPEN"
    }


# ---------------------------------------------------------------
# STEP 2: load_cases() - the quarantine loop
# ---------------------------------------------------------------
# Load what's loadable, quarantine the rest, keep looping no matter what.

def load_cases(path):
    """Read a case CSV and return (good, quarantine): clean dicts and (line, reason, row) tuples."""
    good = []                                           # LIST of clean case dicts
    quarantine = []                                     # LIST of (line number, reason, raw row) for rejected rows

    # "with open(...)" closes the file automatically, even if something crashes.
    # newline="" is what the csv module asks for, so it can handle line endings itself.
    with open(path, newline="") as f:
        reader = csv.reader(f)                          # splits each line into a list of fields,
                                                        # and keeps "OKAFOR, SYLVIA" together because it's in quotes
        next(reader)                                    # read and throw away the header row (line 1)

        # enumerate(..., start=2) numbers the rows starting at 2,
        # because line 1 of the file was the header we just skipped.
        for line_num, row in enumerate(reader, start=2):
            if len(row) == 0:                           # a blank line comes back as an empty list []
                continue                                # it isn't a record at all, so skip it (don't quarantine it)

            try:                                        # attempt the risky thing...
                good.append(parse_row(row))             # ...parse the row and keep it if it worked
            except ValueError as err:                   # catch ONLY ValueError (never a bare except:)
                quarantine.append((line_num, str(err), row))   # log where it was, why it failed, and what it was

    return good, quarantine                             # hand both lists back to the caller


# ---------------------------------------------------------------
# STEP 3: report() - print the counts and the full quarantine log
# ---------------------------------------------------------------

def report(good, quarantine):
    """Print how many rows loaded, how many were quarantined, and why each one was rejected."""
    print(f"Rows loaded cleanly:   {len(good)}")
    print(f"Rows quarantined:      {len(quarantine)}")
    print()                                             # blank line before the log
    print("QUARANTINE LOG - every rejected row, with the reason:")

    for line_num, reason, row in quarantine:            # unpack each (line, reason, row) tuple
        preview = ",".join(row)[:24] + "..."            # glue the fields back together, keep the first 24 characters
        # :>3 right-aligns the line number in 3 spaces; :<50 left-aligns the reason in 50 spaces,
        # so every log line's columns line up.
        print(f"  line {line_num:>3}: {reason:<50} | {preview}")


# ---------------------------------------------------------------
# STEP 4: Run it
# ---------------------------------------------------------------
# __name__ is "__main__" only when you run this file directly
# (python intake_safe.py). When test_intake.py IMPORTS this file,
# __name__ is "intake_safe", so the report does NOT print during tests.

if __name__ == "__main__":
    good, quarantine = load_cases(DATA_FILE)            # load the real file
    report(good, quarantine)                            # print the results
