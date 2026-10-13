import re
from datetime import datetime, date
def clean_case_id(raw_id):           # Define a function that receives a case ID
    raw_id = raw_id.strip().upper()  # Remove outer spaces and convert to uppercase
    match = re.fullmatch(r"CC[- ]?(\d{5})", raw_id)
    if match is None:
        raise ValueError("bad case_id")
    return "CC-" + match.group(1)  # Return the cleaned case ID

def clean_name(raw_name):
    raw_name = raw_name.strip()
    raw_name = " ".join(raw_name.split()) #split the string, then add a space between them
    raw_name = raw_name.title()  # Capitalize the first letter of each word
    return raw_name             # Send the cleaned name back  # Remove spaces at the beginning and end

def clean_sex(raw_sex):                 # Create a function to clean the sex field
    raw_sex = raw_sex.strip().upper()  # Remove outer spaces and make uppercase
    if raw_sex == "M" or raw_sex == "MALE":
        return "M"
    elif raw_sex == "F" or raw_sex == "FEMALE":
        return "F"
    else:
        return "U"

def clean_age(raw_age):
    """Convert a valid age to an integer; otherwise return blank."""
    raw_age = raw_age.strip()
    try:
        age = int(raw_age)             # Convert text into an integer
        if 0 <= age <= 110:           # Valid age range
            return age
    except ValueError:
        pass                          # Invalid number: continue below
    return ""                         # Invalid ages become blank

def clean_status(raw_status):
    status = raw_status.strip().upper()
    if status in ["OPEN", "OPN"]:
        return "OPEN"
    elif status in ["CLOSED", "CLSD", "CLEARED"]:
        return "CLOSED"
    else:
        raise ValueError("bad status")

def clean_beat(raw_beat):
    match = re.search(r"\d{3}", raw_beat)  # Find three digits
    if match:
        return match.group()              # Return the beat number
    return ""                             # No valid beat found

def clean_date(raw_date):
    raw_date = raw_date.strip()
    if raw_date.upper() in ["", "N/A", "UNKNOWN"]:
        raise ValueError("missing date")
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"]
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(raw_date, fmt).date()
            if parsed_date > date(2026, 10, 7):
                raise ValueError("future date")
            return parsed_date.isoformat()
        except ValueError as error:
            if str(error) == "future date":
                raise
    raise ValueError("invalid date")

def clean_phone(tip_notes):
    match = re.search(
        r"(?<!\d)(?:\((\d{3})\)|(\d{3}))[-.\s]*(\d{3})[-.\s]*(\d{4})(?!\d)",
        tip_notes
    )
    if match is None:
        return ""
    area = match.group(1) or match.group(2)
    middle = match.group(3)
    last = match.group(4)
    return f"{area}-{middle}-{last}"

class Case:
    """Represent one cleaned cold case."""
    def __init__(self, case_id, victim_name, sex, age,
                 incident_date, beat, status, callback_phone):
        self.case_id = case_id
        self.victim_name = victim_name
        self.sex = sex
        self.age = age
        self.incident_date = incident_date
        self.year = int(incident_date[:4])
        self.beat = beat
        self.status = status
        self.callback_phone = callback_phone
    @classmethod
    def from_row(cls, row):
        """Create a cleaned Case from a nine-field CSV row."""
        if len(row) != 9:
            raise ValueError("wrong field count")
        return cls(
            clean_case_id(row[0]),
            clean_name(row[1]),
            clean_sex(row[2]),
            clean_age(row[3]),
            clean_date(row[4]),
            clean_beat(row[6]),
            clean_status(row[7]),
            clean_phone(row[8])
        )
    @property
    def years_unsolved(self):
        return 2026 - self.year
    @property
    def is_stale(self):
        return self.status == "OPEN" and self.years_unsolved >= 5
    def to_row(self):
        """Return fields in the required output CSV order."""
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

        
     