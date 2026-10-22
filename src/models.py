# models.py
# The Case class: one cleaned cold case. Case.from_row() turns a messy
# CSV row into a Case by running each column through its cleaner from
# patterns.py. src/intake.py imports this file to load the whole file.

from src.patterns import (     # Bring in the field cleaners from src/patterns.py
    clean_case_id, clean_name, clean_sex, clean_age,
    clean_date, clean_beat, clean_status, clean_phone
)


# ---------------------------------------------------------------------------
# THE CASE CLASS
# A class is a blueprint. Each Case object stores the cleaned fields for
# ONE cold case, and has helpers (years_unsolved, is_stale, to_row).
# ---------------------------------------------------------------------------

class Case:
    """Represent one cleaned cold case."""

    # __init__ runs automatically when a new Case is created.
    # "self" is the specific Case object being built.
    def __init__(self, case_id, victim_name, sex, age,
                 incident_date, beat, status, callback_phone):
        self.case_id = case_id                  # Save each cleaned value onto the object
        self.victim_name = victim_name
        self.sex = sex
        self.age = age
        self.incident_date = incident_date      # Already "YYYY-MM-DD" text at this point
        self.year = int(incident_date[:4])      # [:4] takes the first 4 characters ("2018-03-22" -> "2018"), int() makes it a number
        self.beat = beat
        self.status = status
        self.callback_phone = callback_phone

    # @classmethod means this function is called on the class itself
    # (Case.from_row(row)) instead of on an existing case. "cls" is the
    # Case class, so cls(...) creates a new Case.
    @classmethod
    def from_row(cls, row):
        """Create a cleaned Case from a nine-field CSV row."""
        if len(row) != 9:                       # A good row has exactly 9 columns
            raise ValueError("wrong field count")   # Truncated/broken row -> quarantine
        # Run each column through its cleaner, then build the Case.
        # If ANY cleaner raises ValueError, it stops here and the error
        # travels back to src/intake.py, which quarantines the row.
        return cls(
            clean_case_id(row[0]),   # column 0: case_id
            clean_name(row[1]),      # column 1: victim_name
            clean_sex(row[2]),       # column 2: sex
            clean_age(row[3]),       # column 3: age
            clean_date(row[4]),      # column 4: incident_date
            # column 5 (address) is skipped on purpose: the assignment says to drop it
            clean_beat(row[6]),      # column 6: beat
            clean_status(row[7]),    # column 7: status
            clean_phone(row[8])      # column 8: tip_notes -> we pull out the phone number
        )

    # @property lets you use this like a variable: case.years_unsolved
    # (no parentheses), even though it's calculated each time.
    @property
    def years_unsolved(self):
        """Return how many years have passed since the incident."""
        return 2026 - self.year          # Uses the calendar year only (2021 -> 5 years)

    @property
    def is_stale(self):
        """Return True if the case is OPEN and unsolved for 5+ years."""
        return self.status == "OPEN" and self.years_unsolved >= 5   # Both must be true

    def to_row(self):
        """Return fields in the required output CSV order."""
        # This list becomes one line of cases_clean.csv, so the order
        # must match the header row written in src/intake.py.
        return [
            self.case_id,
            self.victim_name,
            self.sex,
            self.age,
            self.incident_date,
            self.year,
            self.beat,
            self.status,
            self.callback_phone
        ]
