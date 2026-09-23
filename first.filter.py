# ---------- SETTINGS ----------

CURRENT_YEAR = 2026                 # year used to calculate years unsolved
STALE_YEARS = 5                     # case is stale when 5+ years old


# ---------- STEP 1: set up the accumulators BEFORE the loop ----------

total = 0                           # how many good records we parsed
open_count = 0                      # how many cases have status OPEN
stale_count = 0                     # OPEN cases that are 5+ years old
juvenile_count = 0                  # OPEN cases where victim was under 18

oldest_year = CURRENT_YEAR          # start high - older years will be smaller
oldest_name = ""                    # stores the name of the oldest open case


# ---------- STEP 2: open and walk through the file ----------

f = open("wk03_data_raw_cases_50.txt", "r")   # open the evidence file

for line in f:                      # go through the file one line at a time

    line = line.strip()             # remove spaces and newline

    # skip blank lines
    if line == "":                  # check if the line is blank
        continue                    # skip it and go to the next record

    fields = line.split("|")        # split the record using the | symbol

    name = fields[0].strip().title()    # clean name and change to title case
    sex = fields[1].strip().upper()     # clean sex and change to uppercase
    age = int(fields[2].strip())        # clean age and convert to integer
    case_date = fields[3].strip()       # clean the case date
    year = int(case_date[0:4])          # take first 4 characters to get year
    addr = fields[4].strip().title()    # clean address and use title case
    beat = fields[5].strip().title()    # clean beat
    status = fields[6].strip().upper()  # make open/Open/OPEN become OPEN

    years_unsolved = CURRENT_YEAR - year    # calculate how old the case is

    total = total + 1                       # count this record


    # ---------- STEP 3: check OPEN cases ----------

    if status == "OPEN":                    # only check open cases

        open_count = open_count + 1         # count another open case

        if age < 18:                        # check if victim was under 18
            juvenile_count = juvenile_count + 1   # count juvenile open case

        if years_unsolved >= STALE_YEARS:   # check if case is 5+ years old
            stale_count = stale_count + 1   # count another stale case
            flag = "*** STALE ***"          # create stale flag
            print(f"{flag} {name} ({year})") # print the stale open case

        if year < oldest_year:              # is this the oldest case so far?
            oldest_year = year              # remember this year
            oldest_name = name              # remember this person's name


f.close()                                   # close the file


# ---------- STEP 4: print final report ----------

print()                                     # blank line before report
print("FIRST FILTER REPORT")                # report title
print("-------------------")                  # divider
print(f"Total records:       {total}")       # total records
print(f"Open cases:          {open_count}")  # total open cases
print(f"Stale (>= 5 yrs):    {stale_count}") # stale open cases
print(f"Juvenile open cases: {juvenile_count}")  # juvenile open cases
print(f"Oldest open case:    {oldest_name} ({oldest_year})")  # oldest case
