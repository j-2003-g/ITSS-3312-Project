# patterns.py
# The field cleaners: one small function per column of the raw file.
# Most of them use regex to pull a clean value out of messy text.
# models.py uses these to build a Case; tests/test_intake.py tests them.

import re                              # "re" = regular expressions, used to find text patterns like "CC-12345"
from datetime import datetime, date    # datetime reads dates from text; date represents a calendar day


# ---------------------------------------------------------------------------
# FIELD CLEANERS
# Each function takes ONE messy value (a string from the CSV) and returns a
# clean version. If a CRITICAL field can't be fixed, the function "raises"
# a ValueError. That error tells src/intake.py to quarantine (reject) the row.
# ---------------------------------------------------------------------------

def clean_case_id(raw_id):           # Define a function that receives a case ID
    """Normalize a case ID to CC-#####; raise ValueError if it can't be fixed."""
    raw_id = raw_id.strip().upper()  # Remove outer spaces and convert to uppercase ("  cc-123 " -> "CC-123")
    # fullmatch means the WHOLE string must fit this pattern:
    #   CC       -> the letters C and C
    #   [- ]?    -> optionally one dash or one space ("?" means "zero or one")
    #   (\d{5})  -> exactly 5 digits; the ( ) "captures" them so we can reuse them
    match = re.fullmatch(r"CC[- ]?(\d{5})", raw_id)
    if match is None:                # None means the pattern did not fit (e.g. only 4 digits)
        raise ValueError("bad case_id")  # Critical field is broken -> this row gets quarantined
    return "CC-" + match.group(1)  # group(1) is the 5 captured digits; rebuild as "CC-#####"


def clean_name(raw_name):
    """Strip and collapse extra spaces, then convert the name to Title Case."""
    raw_name = raw_name.strip()                # Remove spaces at the beginning and end
    raw_name = " ".join(raw_name.split())      # split() breaks on any run of spaces; join puts ONE space back between pieces
    raw_name = raw_name.title()                # Capitalize the first letter of each word ("walker, g" -> "Walker, G")
    return raw_name                            # Send the cleaned name back


def clean_sex(raw_sex):                 # Create a function to clean the sex field
    """Return M or F; anything else becomes U (unknown)."""
    raw_sex = raw_sex.strip().upper()  # Remove outer spaces and make uppercase ("female" -> "FEMALE")
    if raw_sex == "M" or raw_sex == "MALE":      # Both spellings mean male
        return "M"
    elif raw_sex == "F" or raw_sex == "FEMALE":  # Both spellings mean female
        return "F"
    else:                                        # Blank, "UNK", or anything else
        return "U"                               # U = unknown (not critical, so we keep the row)


def clean_age(raw_age):
    """Convert a valid age to an integer; otherwise return blank."""
    raw_age = raw_age.strip()             # Remove spaces so " 37 " becomes "37"
    try:                                  # "try" = attempt something that might fail
        age = int(raw_age)             # Convert text into an integer (fails for "N/A", "unknown", "?")
        if 0 <= age <= 110:           # Valid age range (999 and -1 are placeholders, so they fail here)
            return age                # Good age: send back the number
    except ValueError:                # int() raises ValueError when the text isn't a whole number
        pass                          # Invalid number: continue below
    return ""                         # Invalid ages become blank (age is not critical, so the row is kept)


def clean_status(raw_status):
    """Map a status to OPEN or CLOSED; raise ValueError for anything else."""
    status = raw_status.strip().upper()          # " open " -> "OPEN", "Closed" -> "CLOSED"
    if status in ["OPEN", "OPN"]:                # "in" checks whether the value is in the list
        return "OPEN"
    elif status in ["CLOSED", "CLSD", "CLEARED"]:  # All three spellings mean the case was solved
        return "CLOSED"
    else:                                        # e.g. "PENDING?", "??", blank
        raise ValueError("bad status")           # Critical field -> quarantine the row


def clean_beat(raw_beat):
    """Return the 3-digit police beat, or blank if there isn't one."""
    # re.search looks ANYWHERE in the text (unlike fullmatch), so it finds
    # the digits inside "beat 631", "Beat 418", or "B-150".
    match = re.search(r"\d{3}", raw_beat)  # Find three digits
    if match:                             # A match object counts as True if something was found
        return match.group()              # Return the beat number (the 3 digits it found)
    return ""                             # No valid beat found -> leave blank (not critical)


def clean_date(raw_date):
    """Convert a date in one of 3 formats to YYYY-MM-DD; raise ValueError if missing, invalid, or in the future."""
    raw_date = raw_date.strip()                       # Remove outer spaces
    if raw_date.upper() in ["", "N/A", "UNKNOWN"]:    # No real date was given
        raise ValueError("missing date")              # Critical field -> quarantine
    # The three allowed date formats, written as strptime "codes":
    #   "%Y-%m-%d"  -> 2018-03-22     (%Y = 4-digit year, %m = month, %d = day)
    #   "%m/%d/%Y"  -> 6/7/2000       (month FIRST, US style)
    #   "%B %d, %Y" -> July 1, 2022   (%B = full month name)
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"]
    for fmt in formats:                               # Try each format, one at a time
        try:
            # strptime = "string parse time": reads the text using this format.
            # It raises ValueError if the text doesn't fit the format OR the
            # date doesn't exist (like Feb 30 or month 13).
            # .date() keeps just the calendar day (drops the time part).
            parsed_date = datetime.strptime(raw_date, fmt).date()
            if parsed_date > date(2026, 10, 7):       # The assignment's "today" is 10/07/2026
                raise ValueError("future date")       # A case can't happen in the future
            return parsed_date.isoformat()            # isoformat() writes the date as "YYYY-MM-DD"
        except ValueError as error:                   # Catches BOTH "wrong format" and our "future date" error
            # Problem: the except above also catches our own "future date" error.
            # If we ignored it, the loop would try the next format and we'd end
            # up reporting "invalid date" instead. So we check the message and
            # re-raise it (send it on up) if it's the future-date error.
            if str(error) == "future date":
                raise                                 # A plain "raise" re-throws the same error
            # Otherwise this format just didn't fit -> loop tries the next one
    raise ValueError("invalid date")                  # None of the 3 formats worked -> quarantine


def clean_phone(tip_notes):
    """Return the first phone number in the tip notes as ###-###-####, or blank."""
    # This regex finds a phone number written in many styles, e.g.
    # "214-555-0202", "214.555.3072", or "(214) 555-4240". Piece by piece:
    #   (?<!\d)              -> the number must NOT come right after another digit
    #   (?:\((\d{3})\)|(\d{3}))
    #                        -> area code: either "(214)" -> group 1, OR "214" -> group 2
    #   [-.\s]*              -> any number of dashes, dots, or spaces between parts
    #   (\d{3})              -> middle 3 digits -> group 3
    #   [-.\s]*              -> separators again
    #   (\d{4})              -> last 4 digits -> group 4
    #   (?!\d)               -> the number must NOT be followed by another digit
    # The two "not next to a digit" checks stop us grabbing part of a longer number.
    match = re.search(                 # search = find the FIRST place the pattern appears
        r"(?<!\d)(?:\((\d{3})\)|(\d{3}))[-.\s]*(\d{3})[-.\s]*(\d{4})(?!\d)",
        tip_notes
    )
    if match is None:                  # No phone number anywhere in the notes
        return ""                      # Leave callback_phone blank
    area = match.group(1) or match.group(2)  # Only one of the two area-code groups is filled; "or" picks that one
    middle = match.group(3)                  # The middle 3 digits
    last = match.group(4)                    # The last 4 digits
    return f"{area}-{middle}-{last}"         # Rebuild in the required format: 214-555-1234
