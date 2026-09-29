# lockers.py - Week 4: Evidence Lockers
# Dedupe the raw case file, profile victim ages, and rank beats by open cases.
#
# Each record has 7 fields separated by "|":
#   [0] name  [1] sex  [2] age  [3] date  [4] address  [5] beat  [6] status


# ---------------------------------------------------------------
# STEP 1: Read the file
# ---------------------------------------------------------------
# "with open(...)" opens the file and closes it automatically when done.
# .readlines() gives back a LIST of strings, one string per line.
with open("wk04_data_raw_cases_dupes.txt") as f:
    raw_lines = f.readlines()


# ---------------------------------------------------------------
# STEP 2: Normalize every line and collect into a LIST
# ---------------------------------------------------------------
# A set only treats strings as duplicates if they match EXACTLY,
# so we clean each line first to make true duplicates identical.
normalized = []                      # empty list to collect cleaned lines

for line in raw_lines:               # visit each raw line one at a time
    clean = line.strip().upper()     # strip = remove edge spaces/newline, upper = ALL CAPS
    if clean == "":                  # skip blank lines so they don't count as records
        continue
    normalized.append(clean)         # add the cleaned line to the end of the list


# ---------------------------------------------------------------
# STEP 3: Dedupe with a SET
# ---------------------------------------------------------------
# A set keeps only one copy of each value, so duplicates vanish.
unique = set(normalized)

lines_in_file = len(normalized)                # how many lines we read (60)
unique_count = len(unique)                     # how many real records (52)
duplicates_removed = lines_in_file - unique_count   # the difference (8)


# ---------------------------------------------------------------
# STEP 4: Loop the UNIQUE records - collect ages, count open cases
# ---------------------------------------------------------------
ages = []        # LIST: every victim age, so we can use min/max/sum/len
per_beat = {}    # DICT: beat number -> how many OPEN cases it has

for rec in unique:                   # loop the deduped records, not the raw ones
    fields = rec.split("|")          # break the record into a list of 7 fields

    age = int(fields[2].strip())     # field 2 is age; strip spaces, convert text -> number
    beat = fields[5].strip().replace("BEAT", "").strip()   # "BEAT 442" -> "442"
    status = fields[6].strip()       # field 6 is "OPEN" or "CLOSED"

    ages.append(age)                 # collect this age into the list

    # The counting pattern: first time we see a key, create it at 1;
    # every time after that, add 1 to it.
    if status == "OPEN":
        if beat in per_beat:
            per_beat[beat] += 1
        else:
            per_beat[beat] = 1


# ---------------------------------------------------------------
# STEP 5: Print the report
# ---------------------------------------------------------------
print("=== EVIDENCE LOCKER REPORT ===")
print()

# Dedupe numbers
print(f"Lines in file:      {lines_in_file}")
print(f"Unique records:     {unique_count}")
print(f"Duplicates removed: {duplicates_removed}")
print()

# Age profile - min, max, sum, and len all work directly on a list.
# :.1f rounds the average to one decimal place.
youngest = min(ages)
oldest = max(ages)
average = sum(ages) / len(ages)
print(f"Youngest {youngest} / Oldest {oldest} / Average {average:.1f}")
print()

# Beat ranking, most open cases first.
#   sorted(per_beat)          -> sorts the dict's KEYS (beat numbers)
#   key=per_beat.get          -> ...but compare them by their VALUES (counts)
#   reverse=True              -> biggest count first
print("Open cases by beat (most burdened first):")
for beat in sorted(per_beat, key=per_beat.get, reverse=True):
    count = per_beat[beat]           # look up this beat's count in the dict
    bar = "#" * count                # repeat "#" count times: 4 -> "####"
    # :<6 left-aligns the beat in 6 spaces, :>3 right-aligns the count in 3
    print(f"Beat {beat:<6}{count:>3}  {bar}")
