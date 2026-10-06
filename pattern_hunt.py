# pattern_hunt.py - Week 5: Pattern Hunters (Operation: Tip Line)
# Mine 24 free-text tips for phones, dates, case refs, and beats,
# then count how many tips left a callback number.
#
# Tips have NO delimiters (no "|"), so split() can't help us.
# Instead we use REGULAR EXPRESSIONS (regex) to describe the SHAPE
# of what we want, and re.findall() hunts for every match.
#
# Design rule: one function, one pattern, one job.

import re    # Python's built-in regular expression module


# ---------------------------------------------------------------
# STEP 1: Extractor functions - one pattern each
# ---------------------------------------------------------------
# re.findall(pattern, text) returns a LIST of every piece of text
# that matches the pattern. No matches -> an empty list [].
# The r"..." (raw string) stops Python from treating "\" as special,
# so the backslashes reach the regex engine untouched.

def extract_phones(text):
    """Return every phone number in text, e.g. (214) 555-1234 or 214-555-1234."""
    # The slide's pattern r"\(?\d{3}\)?[ -]\d{3}-\d{4}" treats each paren
    # as optional on its own, so "Witness (784-550-8605)" comes back as
    # "(784-550-8605" with a stray "(". To fix that, the area code must be
    # EITHER "(214) " OR "214-":
    # (?: ... | ... )  a group of two choices; "|" means OR, and "?:" means
    #                  "don't capture", so findall still returns the whole number
    # \(\d{3}\)        a literal "(", three digits, a literal ")", then a space
    #                  (the \ means the literal character, not regex magic)
    # \d{3}-           OR: three digits followed by a dash
    # \d{3}-\d{4}      then three digits, a dash, and four digits
    return re.findall(r"(?:\(\d{3}\) |\d{3}-)\d{3}-\d{4}", text)


def extract_case_refs(text):
    """Return every case reference in text, e.g. CC-14589."""
    # literal "CC-" followed by exactly five digits
    return re.findall(r"CC-\d{5}", text)


def extract_beats(text):
    """Return every beat number mentioned in text, e.g. 'beat 341' -> '341'."""
    # [Bb]    one character: capital B or lowercase b
    # eat     the literal letters "eat" followed by a space
    # (\d{3}) three digits inside ( ) = a CAPTURE GROUP.
    #         When a pattern has a group, findall returns only the
    #         captured part, so we get "341" instead of "beat 341".
    return re.findall(r"[Bb]eat (\d{3})", text)


def extract_iso_dates(text):
    """Return every ISO date in text, e.g. 2019-02-19 (year-month-day)."""
    # four digits, dash, two digits, dash, two digits
    return re.findall(r"\d{4}-\d{2}-\d{2}", text)


def extract_us_dates(text):
    """Return every US-style date in text, e.g. 4/7/2019 (month/day/year)."""
    # one or two digits, "/", one or two digits, "/", four digits
    return re.findall(r"\d{1,2}/\d{1,2}/\d{4}", text)


# STRETCH: dates written with the month's name.
# Stored once in a variable so both patterns below can reuse it.
# "|" inside a group means OR: January OR February OR ...
# "(?: ... )" is a NON-capturing group: it groups the choices together
# but does NOT trigger findall's "return only the group" behavior,
# so we still get the whole date back.
MONTHS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"


def extract_month_dates(text):
    """Return every month-name date in text, e.g. 'August 13, 2024' or '4 April 2024'."""
    # Form 1: Month Day, Year  ->  "February 15, 2017"
    month_first = re.findall(MONTHS + r" \d{1,2}, \d{4}", text)
    # Form 2: Day Month Year   ->  "15 December 2020"
    day_first = re.findall(r"\d{1,2} " + MONTHS + r" \d{4}", text)
    return month_first + day_first    # + joins the two lists into one


# ---------------------------------------------------------------
# STEP 2: summarize_tip() - calls the extractors, builds one line
# ---------------------------------------------------------------
# Small tools compose into a bigger one. This function doesn't know
# any regex itself; it just asks each extractor for its evidence.

def summarize_tip(number, tip):
    """Return a one-line summary of everything the extractors found in a tip."""
    phones = extract_phones(tip)         # list of phone numbers
    refs = extract_case_refs(tip)        # list of case refs
    beats = extract_beats(tip)           # list of beat numbers
    dates = extract_iso_dates(tip) + extract_us_dates(tip) + extract_month_dates(tip)   # all date formats in one list

    # :>2 right-aligns the tip number in 2 spaces so the columns line up
    return f"TIP {number:>2}: phone={phones} case={refs} beat={beats} date={dates}"


# ---------------------------------------------------------------
# STEP 3: Read the tips
# ---------------------------------------------------------------
with open("wk05_data_tipline.txt") as f:
    raw_lines = f.readlines()            # LIST of strings, one per line

tips = []                                # empty list to collect real tips
for line in raw_lines:                   # visit each line one at a time
    clean = line.strip()                 # remove the newline and edge spaces
    if clean == "":                      # skip blank lines
        continue
    tips.append(clean)                   # keep the tip (case matters for regex here, so no .upper())


# ---------------------------------------------------------------
# STEP 4: Summarize every tip and count callbacks
# ---------------------------------------------------------------
with_callback = 0                        # tips that have at least one phone number

# enumerate() hands back (position, item) pairs; start=1 numbers tips 1..24
for i, tip in enumerate(tips, start=1):
    print(summarize_tip(i, tip))         # one summary line per tip

    if len(extract_phones(tip)) >= 1:    # at least one phone = someone to call back
        with_callback += 1               # add 1 to the running count

no_callback = len(tips) - with_callback  # everything else has no callback


# ---------------------------------------------------------------
# STEP 5: Final report (numbers must match the slide: 24 / 15 / 9)
# ---------------------------------------------------------------
print()                                  # blank line between summaries and report
print(f"Tips processed:       {len(tips)}")
print(f"Tips with a callback: {with_callback}")
print(f"Tips with NO callback: {no_callback}  <- these leads die without follow-up")
