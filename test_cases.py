from case_model import clean_case_id, clean_name, clean_age, clean_status, clean_date
import pytest

def test_valid_case_id():
    result = clean_case_id("cc-12345")
    assert result == "CC-12345"

def test_clean_name():
    assert clean_name("  jOHN   sMITH  ") == "John Smith"

def test_invalid_age():
    assert clean_age("150") == ""

def test_invalid_case_id():
    with pytest.raises(ValueError):
        clean_case_id("CC-1234")

def test_invalid_status():
    with pytest.raises(ValueError):
        clean_status("PENDING")

def test_future_date():
    with pytest.raises(ValueError, match="future date"):
        clean_date("2027-01-01")