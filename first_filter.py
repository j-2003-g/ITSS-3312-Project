DATA_FILE = "wk03_data_raw_cases_50.txt"
CURRENT_YEAR = 2026
STALE_YEARS = 5  # try 3, 5, 10 and watch the stale count move

file = open(DATA_FILE)
records = file.readlines()
file.close()

total_records = 0
open_count = 0
stale_count = 0
juvenile_open_count = 0
oldest_year = CURRENT_YEAR  # start high so the first real case always wins
oldest_name = ""

for line in records:
    line = line.strip()
    if line == "":
        continue  # skip blanks, keep looping

    fields = line.split("|")
    if len(fields) != 7:
        continue  # skip junk rows instead of crashing

    name = fields[0].strip().title()
    age = int(fields[2].strip())
    year = int(fields[3].strip()[0:4])
    status = fields[6].strip().upper()

    total_records += 1
    years_unsolved = CURRENT_YEAR - year

    print(f"{name}: {years_unsolved} years unsolved")

    if years_unsolved >= STALE_YEARS:
        flag = "*** STALE ***"
    elif years_unsolved >= 2:
        flag = "aging"
    else:
        flag = "recent"

    if status == "OPEN" and years_unsolved >= STALE_YEARS:
        print(f"{name} {flag}")

    if status == "OPEN":
        open_count += 1

        if years_unsolved >= STALE_YEARS:
            stale_count += 1

        if age < 18:
            juvenile_open_count += 1

        if year < oldest_year:
            oldest_year = year
            oldest_name = name

print()
print(f"Total records: {total_records}")
print(f"Open cases: {open_count}")
print(f"Stale (>= {STALE_YEARS} yrs): {stale_count}")
print(f"Juvenile open cases: {juvenile_open_count}")
print(f"Oldest open case: {oldest_name} ({oldest_year})")