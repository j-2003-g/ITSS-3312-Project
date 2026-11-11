# test_intake.py
# Automated tests for our cleaner functions. Run them with:
#     pytest          (from the project's top folder)
# pytest finds every function whose name starts with "test_" and runs it.
# A test PASSES if nothing goes wrong, and FAILS if an assert is False
# or an unexpected error happens.

from src.patterns import clean_case_id, clean_name, clean_age, clean_status, clean_date   # The functions we're testing (now in src/patterns.py)
import pytest                                                                            # The testing library

# --- "Happy path" tests: good or fixable input gives the right output ---

def test_valid_case_id():
    result = clean_case_id("cc-12345")    # Lowercase ID should get fixed
    assert result == "CC-12345"           # assert = "this must be True, or the test fails"

def test_clean_name():
    assert clean_name("  jOHN   sMITH  ") == "John Smith"   # Extra spaces removed, Title Case applied

def test_invalid_age():
    assert clean_age("150") == ""         # 150 is outside 0-110, so the age should be blanked

# --- "Failure path" tests: bad input must raise an error (so the row gets quarantined) ---

def test_invalid_case_id():
    with pytest.raises(ValueError):       # This test passes ONLY if the code inside raises ValueError
        clean_case_id("CC-1234")          # Only 4 digits -> can't be fixed

def test_invalid_status():
    with pytest.raises(ValueError):
        clean_status("PENDING")           # Not OPEN or CLOSED -> unknown status

def test_future_date():
    # match="future date" also checks the error MESSAGE, so this proves the
    # row is rejected for the right reason (not just "invalid date")
    with pytest.raises(ValueError, match="future date"):
        clean_date("2027-01-01")          # After the assignment's "today" (10/07/2026)
