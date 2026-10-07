# test_intake.py - Week 6: pytest proof that parse_row() works
# Run with:  python -m pytest test_intake.py
#
# pytest finds every function whose name starts with "test_" and runs it.
# If every assert inside is True, the test passes (a green dot).
# If any assert is False, or an unexpected error happens, it fails.

import pytest                          # the testing library (gives us pytest.raises)
from intake_safe import parse_row      # bring in the function we want to test


def make_good_row():
    """Return a fresh, valid 8-field row (a new list every call, so tests can't affect each other)."""
    # Deliberately messy: extra spaces and lowercase, to prove parse_row cleans them up.
    return ["CC-1", " carter, d ", "m", "36", "2018-03-22", "412 larkmoor", "352", "open"]


def test_good_row_parses():
    """A valid row comes back as a clean dict."""
    case = parse_row(make_good_row())  # parse the good row
    assert case["age"] == 36           # "36" became the number 36
    assert case["name"] == "Carter, D" # spaces stripped, Title Case applied
    assert case["status"] == "OPEN"    # "open" became uppercase


def test_bad_age_rejected():
    """An age of 'unknown' raises ValueError instead of loading."""
    row = make_good_row()              # start from a good row...
    row[3] = "unknown"                 # ...then damage the age field
    with pytest.raises(ValueError):    # this test PASSES only if the code inside raises ValueError
        parse_row(row)


def test_missing_date_rejected():
    """An empty date field raises ValueError instead of loading."""
    row = make_good_row()              # start from a good row...
    row[4] = ""                        # ...then blank out the date
    with pytest.raises(ValueError):    # must raise ValueError to pass
        parse_row(row)

# Note: "with" syntax in Python ensures the file closes even if error occurs
# Note: pytest.raises() is like an assert where it expects an error and fails the test if error is not raised
